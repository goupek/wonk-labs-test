import time as _t

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.helpers import js_click


class PresentationsPage(BasePage):
    """Page object for the presentations gallery and generation flow.

    Flow:
    1. open()                        → /ru/presentations  (template gallery)
    2. select_template_by_name(name) → click "Выбрать шаблон" on the right card
    3. select_lesson_topic(topic)    → click the lesson card in the step panel
    4. click_continue()              → click "Продолжить" (enabled after selection)
    5. wait_for_generation()         → polls until the presentation is ready
    """

    # ── Template gallery ──────────────────────────────────────────────────────
    # Each card has an <h3> with the template name, and a "Выбрать шаблон" btn.
    _TEMPLATE_BTN_TMPL = (
        "//div[.//h3[normalize-space(.)='{name}']]"
        "//button[normalize-space(.)='Выбрать шаблон']"
    )

    # ── Topic selection step (after template is chosen) ───────────────────────
    # Lessons are shown as cards; each has an <h4> with the topic title.
    _LESSON_H4_TMPL = "//h4[contains(normalize-space(.), '{topic}')]"

    # ── Continue / generate button ─────────────────────────────────────────────
    _CONTINUE_BTN = (By.XPATH,
        "//button[.//span[normalize-space(.)='Продолжить']]"
        " | //button[normalize-space(.)='Продолжить']")

    # ── Spinner (generation in progress) ──────────────────────────────────────
    _SPINNER = (By.XPATH, "//*[contains(@class,'animate-spin')]")

    # ── Success indicator ──────────────────────────────────────────────────────
    # After generation the URL should move from the gallery to a detail page.
    _GALLERY_URL_SUFFIX = "/ru/presentations"

    # ─────────────────────────────────────────────────────────────────────────

    def open(self):
        """Navigate to the presentations template gallery."""
        self.go_to("/ru/presentations")

    # ------------------------------------------------------------------
    def select_template_by_name(self, template_name: str):
        """Click 'Выбрать шаблон' on the card whose <h3> matches template_name.

        Retries up to 3 times — React may re-render the grid after mount.
        """
        xpath = self._TEMPLATE_BTN_TMPL.format(name=template_name)
        last_exc = None
        for _ in range(3):
            try:
                btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                js_click(self.driver, btn)
                return
            except Exception as e:
                last_exc = e
                _t.sleep(0.5)
        raise TimeoutError(
            f"Template '{template_name}' button not found / not clickable.\n"
            f"Current URL: {self.driver.current_url}\n"
            f"Last error: {last_exc}"
        )

    # ------------------------------------------------------------------
    def select_lesson_topic(self, topic: str):
        """Click the lesson card whose <h4> contains topic text.

        After the user picks a template, the app shows a panel with existing
        lessons.  The panel may take a moment to load and is typically a list
        of clickable cards each containing an <h4>.  We try several XPath
        strategies to find the right clickable ancestor.
        """
        xpath_h4 = self._LESSON_H4_TMPL.format(topic=topic)

        # Strategy list — most specific first
        card_xpaths = [
            # Anchor wrapping the card (Next.js <Link>)
            f"//a[.//h4[contains(normalize-space(.), '{topic}')]]",
            # Any cursor-pointer container
            f"//*[contains(@class,'cursor-pointer')]"
            f"[.//h4[contains(normalize-space(.), '{topic}')]]",
            # role="button" wrapper
            f"//*[@role='button'][.//h4[contains(normalize-space(.), '{topic}')]]",
            # Plain button
            f"//button[.//h4[contains(normalize-space(.), '{topic}')]]",
        ]

        deadline = _t.time() + 20
        while _t.time() < deadline:
            for xpath in card_xpaths:
                els = self.driver.find_elements(By.XPATH, xpath)
                if els:
                    js_click(self.driver, els[0])
                    return
            _t.sleep(0.5)

        # Last resort: find the <h4>, then JS-walk up to the first
        # interactive ancestor and click it.
        h4_els = self.driver.find_elements(By.XPATH, xpath_h4)
        if h4_els:
            self.driver.execute_script(
                """
                var el = arguments[0];
                for (var i = 0; i < 8; i++) {
                    el = el.parentElement;
                    if (!el) break;
                    var tag = el.tagName.toLowerCase();
                    var role = el.getAttribute('role') || '';
                    var cls  = el.getAttribute('class') || '';
                    if (tag === 'a' || tag === 'button'
                            || role === 'button' || role === 'link'
                            || cls.indexOf('cursor-pointer') !== -1) {
                        el.click();
                        return;
                    }
                }
                // Fallback: click the h4's direct parent
                arguments[0].parentElement.click();
                """,
                h4_els[0],
            )
            return

        # Diagnostic failure
        visible = []
        try:
            all_h4 = self.driver.find_elements(By.TAG_NAME, "h4")
            visible = [(e.text or "").strip() for e in all_h4[:10]]
        except Exception:
            pass
        raise TimeoutError(
            f"Lesson topic card '{topic}' not found in the topic selection panel.\n"
            f"Current URL: {self.driver.current_url}\n"
            f"Visible <h4> texts: {visible}"
        )

    # ------------------------------------------------------------------
    def click_continue(self, timeout: int = 30):
        """Wait for the 'Продолжить' button to become enabled, then click it.

        The button starts disabled="" until a topic is selected.
        """
        def _enabled(d):
            els = d.find_elements(*self._CONTINUE_BTN)
            if not els:
                return False
            btn = els[0]
            if btn.get_attribute("disabled"):
                return False
            return btn

        btn = WebDriverWait(self.driver, timeout).until(_enabled)
        js_click(self.driver, btn)

    # ------------------------------------------------------------------
    def wait_for_generation(self, timeout: int = 300):
        """Wait until the presentation generation finishes.

        Phase 1 – URL change: after clicking Continue the app navigates
                  away from the gallery to a presentation editor/detail page.
        Phase 2 – Spinner appears: the LLM is working.
        Phase 3 – Spinner disappears: generation complete.
        """
        gallery_url = f"{self.base_url}/ru/presentations"

        # Phase 1: wait for navigation away from the gallery
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: (
                    "/presentations" in d.current_url
                    and d.current_url.rstrip("/") != gallery_url
                )
            )
        except Exception:
            pass  # may still be on gallery if app stayed in-place

        # Phase 2: spinner appears (LLM started)
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.find_elements(*self._SPINNER)
            )
        except Exception:
            pass  # generation may finish before a spinner renders

        # Phase 3: spinner disappears (done)
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: not d.find_elements(*self._SPINNER)
            )
        except Exception:
            pass

        _t.sleep(2)  # let React commit the final render

    # ------------------------------------------------------------------
    def get_page_text_snippet(self, chars: int = 500) -> str:
        """Return up to `chars` of the page body text (for diagnostics)."""
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text[:chars]
        except Exception:
            return ""
