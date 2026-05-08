from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.helpers import js_click


class KtpPage(BasePage):
    _DASHBOARD_CARD = (By.XPATH, "//*[normalize-space(text())='Календарно-тематическое планирование']")
    _ADD_BTN = (By.XPATH, "//button[contains(., 'Добавить КТП')]")

    def open_from_dashboard(self):
        """Go to the dashboard and click the KTP card to enter the KTP section."""
        self.go_to("/ru")
        self.click(self._DASHBOARD_CARD)
        self.wait_url("/ru/ktp")              # wait for URL to land on KTP list
        self.find(self._ADD_BTN)             # then wait for the button to be present

    def open_by_id(self, ktp_id: int):
        """Navigate directly to a KTP by its ID."""
        self.go_to(f"/ru/ktp/{ktp_id}")

    def click_add_ktp(self):
        self.click(self._ADD_BTN)

    def open_by_name(self, name: str):
        """Click a KTP in the list by its name and wait for the detail page."""
        import time as _t, re as _re
        _t.sleep(1)  # let the list re-render after modal close
        el = self.find((By.XPATH, f"//*[contains(text(), '{name}')]"))
        js_click(self.driver, el)
        # Wait until the URL contains /ktp/{numeric-id} — confirms KTP detail page
        self.wait.until(lambda d: _re.search(r'/ktp/\d+', d.current_url))

    def click_add_lesson(self):
        self.click((By.XPATH, "//button[contains(., 'Добавить урок')]"))
