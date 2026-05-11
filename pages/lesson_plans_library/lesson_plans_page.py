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
    _SUBJECT_INPUT    = (By.XPATH, "//input[@role='combobox']")
    # Difficulty: Radix Select, default "Все уровни"
    _DIFFICULTY_SELECT = (By.XPATH, "//button[@role='combobox'][contains(., 'Все уровни')]")

    # ── Lesson plan cards — entire <div role="button"> is clickable ────────
    _CARDS = (By.XPATH, "//div[@role='button'][@tabindex='0'][.//h3]")

    def open(self):
        self.go_to("/ru/lesson-plans-library")

    # ── Toolbar ────────────────────────────────────────────────────────────

    def search(self, text: str):
        """Type into the search box and wait briefly for results."""
        inp = self.find(self._SEARCH_INPUT)
        inp.clear()
        inp.send_keys(text)
        time.sleep(0.8)

    def clear_search(self):
        inp = self.find(self._SEARCH_INPUT)
        inp.send_keys(Keys.CONTROL + "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.5)

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
        """Check if the filter panel grid (Предмет / Сложность) is visible."""
        els = self.driver.find_elements(*self._DIFFICULTY_SELECT)
        if not els:
            return False
        return els[0].is_displayed()

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
        option = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 f"//*[@role='option'][normalize-space(.)='{value}']"
                 f" | //*[@role='option'][.//*[normalize-space(text())='{value}']]")
            )
        )
        js_click(self.driver, option)
        time.sleep(0.3)

    # ── Cards ──────────────────────────────────────────────────────────────

    def wait_for_cards(self):
        """Block until at least one lesson plan card has rendered."""
        self.wait.until(EC.presence_of_element_located(self._CARDS))

    def count_cards(self) -> int:
        """Return the number of lesson plan cards currently visible."""
        return len(self.driver.find_elements(*self._CARDS))

    def get_card_titles(self) -> list:
        """Return a list of all visible card title strings."""
        cards = self.driver.find_elements(*self._CARDS)
        titles = []
        for card in cards:
            try:
                h3 = card.find_element(By.TAG_NAME, "h3")
                titles.append(h3.text.strip())
            except Exception:
                pass
        return titles

    def click_first_card(self):
        """Click the first lesson plan card and wait for detail page."""
        import re as _re
        cards = self.wait.until(EC.presence_of_all_elements_located(self._CARDS))
        js_click(self.driver, cards[0])
        # Detail page URL: /ru/lesson-plans-library/{id}
        self.wait.until(
            lambda d: _re.search(r'/lesson-plans-library/\w+', d.current_url)
                      and d.current_url != f"{self.base_url}/ru/lesson-plans-library"
        )

    def click_card_by_title(self, title: str):
        """Click a card matching the given title text."""
        import re as _re
        locator = (By.XPATH, f"//div[@role='button'][.//h3[contains(., '{title}')]]")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        js_click(self.driver, el)
        self.wait.until(
            lambda d: _re.search(r'/lesson-plans-library/\w+', d.current_url)
                      and d.current_url != f"{self.base_url}/ru/lesson-plans-library"
        )
