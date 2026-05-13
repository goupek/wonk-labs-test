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

    def open_by_name(self, name: str, subject: str = "",
                     grade: str = "", quarter: str = ""):
        """Navigate to a KTP detail page.

        The KTP list view in this app shows each card by its classification
        (Subject + Grade-number + Quarter-number), e.g. "Алгебра 8 4",
        NOT by the topic name typed in the form.  We therefore search by
        the displayed triplet when subject/grade/quarter are supplied;
        we still fall back to the topic name in case the UI changes.

        Handles two app behaviours:
        A) App auto-navigates to the detail page after creation — URL
           contains /ktp/<id>, so we return immediately.
        B) App stays on the list — poll until the KTP card appears, click it.
        """
        import time as _t, re as _re

        # Build the search needles.  Strip "класс" / "четверть" so we
        # only have the numeric parts that appear on the card.
        grade_num = _re.search(r"\d+", grade).group() if grade else ""
        quarter_num = _re.search(r"\d+", quarter).group() if quarter else ""

        # Primary search terms (in priority order)
        search_terms = []
        if subject and grade_num and quarter_num:
            # Most specific: card shows "Алгебра 8 4" — search with both
            # space- and arbitrary-whitespace tolerance via normalize-space
            search_terms.append(f"{subject} {grade_num} {quarter_num}")
        if subject and grade_num:
            search_terms.append(f"{subject} {grade_num}")
        # Fallback to the topic name
        if name:
            search_terms.append(name)

        # Poll for up to 3 s for the app to auto-navigate to the detail page.
        # Many times modal.submit() redirects directly to /ru/ktp/<id>.
        for _ in range(6):
            _t.sleep(0.5)
            if _re.search(r'/ktp/\d+', self.driver.current_url):
                return  # Case A: already on the detail page

        # Still on the list page after 3 s.
        # Force a fresh list load — the dev backend sometimes doesn't
        # auto-refresh the list after a KTP is created.  Navigating
        # explicitly to /ru/ktp triggers a clean fetch.
        self.driver.get(f"{self.base_url}/ru/ktp")
        _t.sleep(2)

        # Scroll to the bottom in case the new KTP is lazy-loaded below the fold.
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        _t.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
        _t.sleep(0.5)

        def _try_click(timeout_s: float) -> bool:
            """Search the list page for the KTP card and click it.

            Uses several XPath strategies × several search terms.  Terms
            in ``search_terms`` are tried in priority order (most specific
            first), each against multiple element kinds.
            """
            xpath_templates = [
                # 1. Anchor wrapping the card (Next.js Link)
                "//a[contains(normalize-space(.), '{t}')]",
                # 2. Clickable card div (cursor-pointer pattern)
                "//*[contains(@class,'cursor-pointer')]"
                "[contains(normalize-space(.), '{t}')]",
                # 3. Button or role-based interactive elements
                "//button[contains(normalize-space(.), '{t}')]",
                "//*[@role='link' or @role='button']"
                "[contains(normalize-space(.), '{t}')]",
                # 4. Any element whose normalized subtree text contains it
                "//*[contains(normalize-space(.), '{t}')]",
            ]
            end = _t.time() + timeout_s
            while _t.time() < end:
                for term in search_terms:
                    for tpl in xpath_templates:
                        xpath = tpl.format(t=term)
                        els = self.driver.find_elements(By.XPATH, xpath)
                        if not els:
                            continue
                        # Pick the smallest match (most specific node).
                        best = min(
                            els,
                            key=lambda e: len((e.text or "").strip()) or 10**9,
                        )
                        self.driver.execute_script(
                            """
                            var el = arguments[0];
                            var t = el.closest(
                                'a,[role="link"],[role="button"],button,'
                                + '[onclick],[class*="cursor-pointer"]'
                            ) || el;
                            t.click();
                            """,
                            best,
                        )
                        return True
                _t.sleep(0.5)
            return False

        # Case B: poll the list for up to 10 s.  If still not found, refresh
        # the list (server may have lagged on returning the new KTP) and
        # poll again for another 15 s.
        clicked = _try_click(10)
        if not clicked:
            self.driver.refresh()
            _t.sleep(2)
            # Refresh may have landed us on the detail page if the app
            # remembers the most recently created KTP — check Case A again
            if _re.search(r'/ktp/\d+', self.driver.current_url):
                return
            clicked = _try_click(15)

        if not clicked:
            # Diagnostic: dump what IS on the page
            body_text = ""
            try:
                body_text = self.driver.find_element(
                    By.TAG_NAME, "body"
                ).text[:600]
            except Exception:
                pass
            visible_names = []
            try:
                # Collect text from clickable card-like elements
                cards = self.driver.find_elements(
                    By.XPATH,
                    "//a[.//h2 or .//h3 or .//h4]"
                    " | //*[contains(@class,'cursor-pointer')]"
                )
                for c in cards[:10]:
                    txt = (c.text or "").strip()
                    if txt:
                        visible_names.append(txt[:80])
            except Exception:
                pass
            raise TimeoutError(
                f"KTP card '{name}' not found in the list after 25 s "
                f"(including one refresh).\n"
                f"Current URL: {self.driver.current_url}\n"
                f"Visible card text samples: {visible_names}\n"
                f"Page body (first 600 chars): {body_text!r}"
            )

        # Wait up to 5 s for the URL to contain /ktp/{numeric-id}.
        # Successful clicks navigate within ~1 s; failing fast here lets
        # the test-level retry try a different KTP name sooner.
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(self.driver, 5).until(
            lambda d: _re.search(r'/ktp/\d+', d.current_url)
        )

    def click_add_lesson(self):
        self.click((By.XPATH, "//button[contains(., 'Добавить урок')]"))
