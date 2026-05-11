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
        """Click a KTP in the list by its name and wait for the detail page.

        Strategy:
        1. Prefer an <a> tag that wraps the card (Next.js Link pattern).
        2. Fall back to any text node containing the name, then use JS
           .closest() to walk up to the nearest interactive ancestor so
           React onClick / Next.js router fires correctly.
        """
        import time as _t, re as _re
        _t.sleep(1)  # let the list re-render after modal close

        # 1. Try <a> link first — covers the Next.js <Link> wrapper pattern
        links = self.driver.find_elements(
            By.XPATH, f"//a[contains(normalize-space(.), '{name}')]"
        )
        if links:
            js_click(self.driver, links[0])
        else:
            # 2. Find the text node and click its nearest interactive ancestor
            el = self.find((By.XPATH, f"//*[contains(text(), '{name}')]"))
            self.driver.execute_script(
                """
                var el = arguments[0];
                var target = el.closest('a, [role="link"], [role="button"], button') || el;
                target.click();
                """,
                el,
            )

        # Wait until the URL contains /ktp/{numeric-id}
        self.wait.until(lambda d: _re.search(r'/ktp/\d+', d.current_url))

    def click_add_lesson(self):
        self.click((By.XPATH, "//button[contains(., 'Добавить урок')]"))
