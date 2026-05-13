import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage
from utils.helpers import js_click


class LessonPlansPage(BasePage):
    # ── Toolbar ────────────────────────────────────────────────────────────
    _SEARCH_INPUT = (By.XPATH, "//input[@placeholder='Поиск по названию или тегам...']")
    _FILTER_BTN   = (By.XPATH, "//button[contains(., 'Фильтры')]")
    # Native <select> — not Radix
    _SORT_SELECT  = (By.XPATH, "//select[.//option[contains(.,'Сначала новые')]]")

    # ── Filter panel ───────────────────────────────────────────────────────
    # Subject: plain combobox input
    _SUBJECT_INPUT = (By.XPATH, "//input[@role='combobox']")
    # Difficulty: Radix Select — exclude language combobox which lives in <header>
    _DIFFICULTY_SELECT = (By.XPATH,
        "//button[@role='combobox'][not(ancestor::header)]")

    # ── Lesson plan cards — entire <div role="button"> is clickable ────────
    _CARDS = (By.XPATH, "//div[@role='button'][@tabindex='0'][.//h3]")

    # ── Card detail MODAL (opens on card click — stays on same URL) ────────
    # Modal container identified by the gradient "Посмотреть план урока" button
    _MODAL_VIEW_BTN  = (By.XPATH, "//button[contains(., 'Посмотреть план урока')]")
    # XPath cannot traverse into SVG namespace elements (.//svg won't work),
    # so we match by the button's own Tailwind size classes (h-8 w-8) which are
    # unique to the modal close button.
    _MODAL_CLOSE_BTN = (By.XPATH,
        "//button[contains(@class,'h-8') and contains(@class,'w-8')]")
    _MODAL_TITLE     = (By.XPATH,
        "//div[contains(@class,'rounded-2xl')]//h2")

    def open(self):
        self.go_to("/ru/lesson-plans-library")

    # ── Toolbar ────────────────────────────────────────────────────────────

    def search(self, text: str):
        """Type into the search box and wait briefly for results."""
        inp = self.find(self._SEARCH_INPUT)
        inp.click()
        inp.send_keys(Keys.CONTROL + "a")
        inp.send_keys(text)
        time.sleep(0.8)

    def clear_search(self):
        """Clear the React-controlled search input and trigger a re-fetch.

        React controlled inputs ignore element.clear() / Keys.DELETE because
        those don't fire the synthetic onChange event.  Use the native value
        property setter + dispatch 'input' event so React detects the change.
        """
        inp = self.find(self._SEARCH_INPUT)
        self.driver.execute_script(
            """
            var el = arguments[0];
            var setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            setter.call(el, '');
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            inp,
        )
        time.sleep(0.8)

    def click_filters(self):
        """Toggle the filter panel."""
        self.click(self._FILTER_BTN)
        time.sleep(0.4)

    def sort_by(self, option_text: str):
        """Change the sort order via the native <select>.

        Valid values: 'Сначала новые', 'Сначала старые', 'По использованию'
        """
        el = self.find(self._SORT_SELECT)
        Select(el).select_by_visible_text(option_text)
        time.sleep(0.5)

    # ── Filter panel ───────────────────────────────────────────────────────

    def is_filter_panel_visible(self) -> bool:
        """Check if the filter panel (Сложность combobox) is visible."""
        els = self.driver.find_elements(*self._DIFFICULTY_SELECT)
        return bool(els) and els[0].is_displayed()

    def fill_subject_filter(self, text: str):
        """Type into the Предмет combobox."""
        inp = self.find(self._SUBJECT_INPUT)
        inp.clear()
        inp.send_keys(text)
        time.sleep(0.5)

    def select_difficulty(self, value: str):
        """Open the Сложность Radix Select and pick an option.

        Valid values: 'Все уровни', 'Легкий', 'Средний', 'Сложный'
        """
        self.click(self._DIFFICULTY_SELECT)
        # Radix options have tabindex="-1" and cursor-default so
        # element_to_be_clickable can stall; presence_of is sufficient.
        option = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[@role='option'][normalize-space(.)='{value}']")
            )
        )
        js_click(self.driver, option)
        time.sleep(0.5)

    # ── Cards ──────────────────────────────────────────────────────────────

    def wait_for_cards(self):
        """Block until at least one lesson plan card has rendered."""
        self.wait.until(EC.presence_of_element_located(self._CARDS))

    def count_cards(self) -> int:
        """Return the number of lesson plan cards currently visible."""
        return len(self.driver.find_elements(*self._CARDS))

    def get_card_titles(self) -> list:
        """Return a list of all visible card title strings."""
        titles = []
        for card in self.driver.find_elements(*self._CARDS):
            try:
                titles.append(card.find_element(By.TAG_NAME, "h3").text.strip())
            except Exception:
                pass
        return titles

    def click_first_card(self):
        """Click the first card — opens a detail MODAL (URL does not change)."""
        cards = self.wait.until(EC.presence_of_all_elements_located(self._CARDS))
        js_click(self.driver, cards[0])
        # Wait for the modal's "Посмотреть план урока" button to appear
        self.wait.until(EC.presence_of_element_located(self._MODAL_VIEW_BTN))
        # Let the modal animation complete so subsequent clicks register correctly
        time.sleep(0.5)

    def close_modal(self):
        """Close the lesson plan preview modal via the X button."""
        # Use presence_of_element_located (not element_to_be_clickable) so animated
        # modals don't stall; js_click bypasses any overlay interception.
        close_btn = self.find(self._MODAL_CLOSE_BTN)
        js_click(self.driver, close_btn)
        self.wait.until(EC.invisibility_of_element_located(self._MODAL_VIEW_BTN))

    def click_view_lesson_plan(self):
        """Click 'Посмотреть план урока' inside the modal — navigates to detail page.

        The detail page URL varies (e.g. /ru/lesson-plan-editor/<id>), so we only
        assert that the URL changed away from the list page.

        Uses find() + js_click instead of click() because the button may be clipped
        by the modal's overflow-y-auto container, causing EC.element_to_be_clickable
        to return False even when the button is in the DOM.  js_click scrolls it
        into view and fires a native click that reaches the React handler.
        """
        url_before = self.driver.current_url
        view_btn = self.find(self._MODAL_VIEW_BTN)
        js_click(self.driver, view_btn)
        self.wait.until(lambda d: d.current_url != url_before)
