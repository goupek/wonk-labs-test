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

    # ── Filter panel ───────────────────────────────────────────────────────
    # Subject uses a plain text input with role="combobox"
    _SUBJECT_INPUT = (By.XPATH, "//input[@role='combobox']")
    _CLASS_SELECT  = (By.XPATH, "//button[@role='combobox'][contains(., 'Все классы')]")
    _TYPE_SELECT   = (By.XPATH, "//button[@role='combobox'][contains(., 'Все типы')]")
    _LANG_SELECT   = (By.XPATH, "//button[@role='combobox'][contains(., 'Все языки')]")
    _VIS_SELECT    = (By.XPATH, "//button[@role='combobox'][contains(., 'Все материалы')]")

    # ── Material cards ─────────────────────────────────────────────────────
    _OPEN_BTNS     = (By.XPATH, "//button[contains(., 'Открыть')]")
    # Edit button has no aria-label — identified by the square-pen SVG icon class
    _EDIT_BTNS     = (By.XPATH, "//button[.//*[contains(@class,'lucide-square-pen')]]")
    _DOWNLOAD_BTNS = (By.XPATH, "//button[@aria-label='Скачать материал']")
    _PDF_BTNS      = (By.XPATH, "//button[@aria-label='Скачать PDF']")

    # ── Pagination — uses <a> tags, not <button> ───────────────────────────
    _PREV_BTN  = (By.XPATH, "//nav[@aria-label='pagination']//a[@aria-label='Go to previous page']")
    _NEXT_BTN  = (By.XPATH, "//nav[@aria-label='pagination']//a[@aria-label='Go to next page']")
    _PAGE_LINKS = (By.XPATH, "//nav[@aria-label='pagination']//a[@data-slot='pagination-link']")

    # ── Upload modal ───────────────────────────────────────────────────────
    _UPLOAD_MODAL_TITLE  = (By.XPATH, "//*[contains(text(),'Загрузить материал') or contains(text(),'Загрузка')]")
    _UPLOAD_CLOSE_BTN    = (By.XPATH, "//button[@aria-label='Close'] | //button[contains(@class,'close')] | //button[contains(.,'Отмена')]")

    def open(self):
        self.go_to("/ru/library")

    # ── Toolbar actions ────────────────────────────────────────────────────

    def click_filters(self):
        """Toggle the filter panel."""
        self.click(self._FILTER_BTN)

    def click_grid_view(self):
        self.click(self._GRID_BTN)

    def click_list_view(self):
        self.click(self._LIST_BTN)

    def click_upload(self):
        self.click(self._UPLOAD_BTN)

    # ── Filter panel actions ───────────────────────────────────────────────

    def is_filter_panel_visible(self) -> bool:
        """Return True if the subject filter input is in the DOM and visible."""
        els = self.driver.find_elements(*self._SUBJECT_INPUT)
        return bool(els) and els[0].is_displayed()

    def fill_subject_filter(self, text: str):
        inp = self.find(self._SUBJECT_INPUT)
        inp.clear()
        inp.send_keys(text)

    def select_class_filter(self, value: str):
        """Open the 'Класс' combobox and pick an option by visible text."""
        self._select_combobox(self._CLASS_SELECT, value)

    def select_type_filter(self, value: str):
        self._select_combobox(self._TYPE_SELECT, value)

    def select_language_filter(self, value: str):
        self._select_combobox(self._LANG_SELECT, value)

    def select_visibility_filter(self, value: str):
        self._select_combobox(self._VIS_SELECT, value)

    # ── Card actions ───────────────────────────────────────────────────────

    def count_cards(self) -> int:
        """Return the number of 'Открыть' buttons visible (≈ number of cards)."""
        return len(self.driver.find_elements(*self._OPEN_BTNS))

    def click_open_first(self):
        """Click the first 'Открыть' button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._OPEN_BTNS))
        js_click(self.driver, btns[0])

    def click_edit_first(self):
        """Click the first edit (pencil) button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._EDIT_BTNS))
        js_click(self.driver, btns[0])

    def click_download_first(self):
        """Click the first download button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._DOWNLOAD_BTNS))
        js_click(self.driver, btns[0])

    def click_pdf_first(self):
        """Click the first 'Скачать PDF' button."""
        btns = self.wait.until(EC.presence_of_all_elements_located(self._PDF_BTNS))
        js_click(self.driver, btns[0])

    # ── Pagination ─────────────────────────────────────────────────────────

    def go_next_page(self):
        """Click the 'Вперед' (Next) pagination link."""
        el = self.wait.until(EC.element_to_be_clickable(self._NEXT_BTN))
        js_click(self.driver, el)
        time.sleep(1)  # let the new page of cards render

    def go_prev_page(self):
        """Click the 'Назад' (Prev) pagination link (only when not disabled)."""
        el = self.wait.until(EC.element_to_be_clickable(self._PREV_BTN))
        js_click(self.driver, el)
        time.sleep(1)

    def go_to_page(self, page_number: int):
        """Click a numbered pagination link by its visible number."""
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
        """Try the close / cancel button; fall back to Escape."""
        try:
            self.click(self._UPLOAD_CLOSE_BTN)
        except Exception:
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    # ── Internal helpers ───────────────────────────────────────────────────

    def _select_combobox(self, trigger_locator, option_text: str):
        """Open a Radix-style combobox and select an option by text."""
        self.click(trigger_locator)
        option = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[@role='option' or @role='listbox']//*[normalize-space(text())='{option_text}']"
                           f" | //*[@role='option'][normalize-space(text())='{option_text}']")
            )
        )
        js_click(self.driver, option)
