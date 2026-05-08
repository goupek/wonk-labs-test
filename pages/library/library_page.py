import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.helpers import js_click


class LibraryPage(BasePage):
    # ── Toolbar ────────────────────────────────────────────────────────────
    _FILTER_BTN    = (By.XPATH, "//button[contains(., 'Фильтры')]")
    _GRID_BTN      = (By.XPATH, "//button[contains(., 'Сетка')]")
    _LIST_BTN      = (By.XPATH, "//button[contains(., 'Список')]")
    _UPLOAD_BTN    = (By.XPATH, "//button[contains(., 'Загрузить')]")

    # ── Filter panel — identified by its section id ────────────────────────
    _FILTER_SECTION = (By.ID, "library-filters-panel")
    _SUBJECT_INPUT  = (By.XPATH, "//input[@role='combobox']")
    _CLASS_SELECT   = (By.XPATH, "//button[@role='combobox'][contains(., 'Все классы')]")
    _TYPE_SELECT    = (By.XPATH, "//button[@role='combobox'][contains(., 'Все типы')]")
    _LANG_SELECT    = (By.XPATH, "//button[@role='combobox'][contains(., 'Все языки')]")
    _VIS_SELECT     = (By.XPATH, "//button[@role='combobox'][contains(., 'Все материалы')]")

    # ── Material cards ─────────────────────────────────────────────────────
    _OPEN_BTNS     = (By.XPATH, "//button[contains(., 'Открыть')]")
    _EDIT_BTNS     = (By.XPATH, "//button[.//*[contains(@class,'lucide-square-pen')]]")
    _DOWNLOAD_BTNS = (By.XPATH, "//button[@aria-label='Скачать материал']")
    _PDF_BTNS      = (By.XPATH, "//button[@aria-label='Скачать PDF']")

    # ── Preview modal (opened by Открыть) ──────────────────────────────────
    _PREVIEW_MODAL = (By.XPATH, "//*[@role='dialog'] | //*[contains(@class,'preview')] | //*[contains(@class,'modal')]")

    # ── Pagination — uses <a> tags, not <button> ───────────────────────────
    _PREV_BTN   = (By.XPATH, "//nav[@aria-label='pagination']//a[@aria-label='Go to previous page']")
    _NEXT_BTN   = (By.XPATH, "//nav[@aria-label='pagination']//a[@aria-label='Go to next page']")
    _PAGE_LINKS = (By.XPATH, "//nav[@aria-label='pagination']//a[@data-slot='pagination-link']")

    # ── Upload modal ───────────────────────────────────────────────────────
    _UPLOAD_MODAL_TITLE = (By.XPATH, "//*[contains(text(),'Загрузить материал') or contains(text(),'Загрузка')]")
    _UPLOAD_CLOSE_BTN   = (By.XPATH, "//button[@aria-label='Close'] | //button[contains(@class,'close')] | //button[contains(.,'Отмена')]")

    def open(self):
        self.go_to("/ru/library")

    # ── Toolbar actions ────────────────────────────────────────────────────

    def click_filters(self):
        """Toggle the filter panel open/closed."""
        self.click(self._FILTER_BTN)

    def click_grid_view(self):
        self.click(self._GRID_BTN)

    def click_list_view(self):
        self.click(self._LIST_BTN)

    def click_upload(self):
        self.click(self._UPLOAD_BTN)

    # ── Filter panel ───────────────────────────────────────────────────────

    def is_filter_panel_visible(self) -> bool:
        """Return True when the filter panel is fully open (opacity 1, height > 0).

        The panel animates open/closed — use computed style rather than
        is_displayed() which doesn't account for animated height.
        """
        els = self.driver.find_elements(*self._FILTER_SECTION)
        if not els:
            return False
        opacity = self.driver.execute_script(
            "return window.getComputedStyle(arguments[0]).opacity;", els[0]
        )
        height = self.driver.execute_script(
            "return arguments[0].getBoundingClientRect().height;", els[0]
        )
        try:
            return float(opacity) > 0.5 and float(height) > 10
        except (ValueError, TypeError):
            return False

    def fill_subject_filter(self, text: str):
        inp = self.find(self._SUBJECT_INPUT)
        inp.clear()
        inp.send_keys(text)

    def select_class_filter(self, value: str):
        self._radix_select(self._CLASS_SELECT, value)

    def select_type_filter(self, value: str):
        self._radix_select(self._TYPE_SELECT, value)

    def select_language_filter(self, value: str):
        self._radix_select(self._LANG_SELECT, value)

    def select_visibility_filter(self, value: str):
        self._radix_select(self._VIS_SELECT, value)

    # ── Card actions ───────────────────────────────────────────────────────

    def wait_for_cards(self):
        """Block until at least one material card has rendered."""
        self.wait.until(EC.presence_of_element_located(self._OPEN_BTNS))

    def count_cards(self) -> int:
        """Return the number of visible material cards."""
        return len(self.driver.find_elements(*self._OPEN_BTNS))

    def click_open_first(self):
        """Click the first 'Открыть' button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._OPEN_BTNS))
        js_click(self.driver, btns[0])

    def click_edit_first(self):
        """Click the first edit (pencil) icon button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._EDIT_BTNS))
        js_click(self.driver, btns[0])

    def click_download_first(self):
        """Click the first 'Скачать материал' button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._DOWNLOAD_BTNS))
        js_click(self.driver, btns[0])

    def click_pdf_first(self):
        """Click the first 'Скачать PDF' button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._PDF_BTNS))
        js_click(self.driver, btns[0])

    def wait_preview_modal(self):
        """Wait for the material preview modal to appear."""
        self.find(self._PREVIEW_MODAL)

    # ── Pagination ─────────────────────────────────────────────────────────

    def go_next_page(self):
        """Click the 'Вперед' (Next) pagination link."""
        el = self.wait.until(EC.element_to_be_clickable(self._NEXT_BTN))
        js_click(self.driver, el)
        time.sleep(1)

    def go_prev_page(self):
        """Click the 'Назад' (Prev) pagination link (only when enabled)."""
        el = self.wait.until(EC.element_to_be_clickable(self._PREV_BTN))
        js_click(self.driver, el)
        time.sleep(1)

    def go_to_page(self, page_number: int):
        """Click a numbered pagination link."""
        locator = (By.XPATH,
                   f"//nav[@aria-label='pagination']"
                   f"//a[@data-slot='pagination-link']"
                   f"[normalize-space(text())='{page_number}']")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        js_click(self.driver, el)
        time.sleep(1)

    # ── Upload modal ───────────────────────────────────────────────────────

    def wait_upload_modal_open(self):
        self.find(self._UPLOAD_MODAL_TITLE)

    def close_upload_modal(self):
        """Try Cancel button first, fall back to Escape."""
        try:
            self.click(self._UPLOAD_CLOSE_BTN)
        except Exception:
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    # ── Internal helpers ───────────────────────────────────────────────────

    def ensure_filter_panel_open(self):
        """Open the filter panel if it is currently closed, then wait for it
        to be fully animated in (comboboxes clickable)."""
        if not self.is_filter_panel_visible():
            self.click(self._FILTER_BTN)
        # Wait until the CLASS combobox is actually clickable inside the panel
        self.wait.until(EC.element_to_be_clickable(self._CLASS_SELECT))

    def _radix_select(self, trigger_locator, option_text: str):
        """Open a Radix UI Select and pick an option.

        Uses normalize-space(.) on the option element itself so it matches
        whether the text sits directly in the item or inside a child span.
        Falls back to the child-element form used by the KTP modal, covering
        both Radix Select variants in use across the app.
        """
        self.click(trigger_locator)
        option = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 f"//*[@role='option'][normalize-space(.)='{option_text}']"
                 f" | //*[@role='option'][.//*[normalize-space(text())='{option_text}']]")
            )
        )
        js_click(self.driver, option)
