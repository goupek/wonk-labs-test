from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.helpers import js_click

# XPath that matches the "Generate lesson plan" / "Сгенерировать КСП" button.
# Targets the gradient button that has non-empty text — language-independent.
_GRADIENT_BTN_XPATH = "//button[contains(@class,'from-[#6360FF]') and normalize-space(.) != '']"


class LessonPage(BasePage):
    _GENERATE_BTN      = (By.XPATH, "//button[contains(., 'Сгенерировать') and not(contains(., 'КСП'))]")
    _LEARNING_OBJ_TA   = (By.XPATH, "//textarea[contains(@placeholder, 'цели обучения')]")
    _LESSON_GOAL_TA    = (By.XPATH, "//textarea[contains(@placeholder, 'основная цель')]")
    _VALUE_TA          = (By.XPATH, "//textarea[contains(@placeholder, 'ценность')]")
    _ASSESSMENT_TA     = (By.XPATH, "//textarea[contains(@placeholder, 'критериям')]")
    _SPECIAL_NEEDS_TA  = (By.XPATH, "//textarea[contains(@placeholder, 'особые потребности')]")
    # Gradient button — spans say "Generate lesson plan" / "Сгенерировать КСП" depending on locale
    _GENERATE_PLAN_BTN = (By.XPATH, _GRADIENT_BTN_XPATH)

    # ── Lesson plan card (shown after generation) ──────────────────────────
    # The card that shows "Поурочный план" with a status badge and Edit button
    # Use contains(text(), ...) so an element with a child icon doesn't break match
    _PLAN_READY_STATUS = (By.XPATH,
        "//*[contains(text(),'Готово') or contains(text(),'Дайын')]")
    _EDIT_PLAN_BTN     = (By.XPATH,
        "//button[normalize-space(.)='Редактировать' or normalize-space(.)='Өңдеу']")

    def click_generate(self):
        """Click 'Сгенерировать' to open the lesson plan form.

        The dev backend sometimes swallows the click and the form never
        opens.  We give it three tries: each click is followed by a short
        wait for the first textarea to appear; if it doesn't, we click
        the button again.
        """
        import time as _t
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # If the form is already open (e.g. previous interaction left it
        # in this state), skip the click.
        if self.driver.find_elements(*self._LEARNING_OBJ_TA):
            return

        last_exc = None
        for attempt in range(3):
            try:
                self.click(self._GENERATE_BTN)
            except Exception as e:
                last_exc = e

            # Short wait for the form to open
            try:
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located(self._LEARNING_OBJ_TA)
                )
                return  # form opened — success
            except Exception as e:
                last_exc = e
                _t.sleep(0.5)  # brief pause before retrying the click

        # Final attempt — let the normal find() raise so the test gets
        # a clear timeout message
        self.find(self._LEARNING_OBJ_TA)

    def fill_learning_objectives(self, text: str):
        self._fill(self._LEARNING_OBJ_TA, text)

    def fill_lesson_goal(self, text: str):
        self._fill(self._LESSON_GOAL_TA, text)

    def fill_value(self, text: str):
        self._fill(self._VALUE_TA, text)

    def fill_assessment_criteria(self, text: str):
        self._fill(self._ASSESSMENT_TA, text)

    def fill_special_needs(self, text: str):
        self._fill(self._SPECIAL_NEEDS_TA, text)

    def generate_plan(self):
        """Click the Generate lesson plan button, retry on backend error,
        then keep the browser open for 5 minutes so the result is visible.

        Retry logic:
        - After clicking, wait up to 8s for a success signal (spinner) or
          an error indicator on the page.
        - If an error toast/banner appears, reload the lesson page, reopen
          the form, and click generate again (up to 3 attempts total).
        - After a successful click, hold the browser open for 5 minutes.
        """
        import time as _t

        # XPath patterns that indicate a backend error response in the UI
        _ERROR_XPATH = (
            "//*[contains(@class,'toast') or contains(@class,'error') or "
            "contains(@class,'alert')]"
            "[contains(.,'404') or contains(.,'ошибка') or "
            "contains(.,'қате') or contains(.,'Not Found') or "
            "contains(.,'не найден')]"
        )

        for attempt in range(3):
            btn = self.wait.until(EC.element_to_be_clickable(self._GENERATE_PLAN_BTN))
            js_click(self.driver, btn)

            # Give the server up to 8s to respond
            _t.sleep(8)

            errors = self.driver.find_elements(By.XPATH, _ERROR_XPATH)
            if not errors:
                break  # no visible error — generation started or finished

            # Error detected — reload the lesson page and try again
            self.driver.refresh()
            _t.sleep(2)
            try:
                self.click(self._GENERATE_BTN)      # reopen the form
                self.find(self._LEARNING_OBJ_TA)    # wait for textareas
            except Exception:
                pass  # form may already be open after refresh

        # Wait up to 5 minutes for generation to complete.
        # Phase 1: spinner appears  (LLM latency — may be skipped if very fast)
        # Phase 2: spinner disappears  (generation done)
        # Return immediately once done so the caller can inspect the result.
        try:
            WebDriverWait(self.driver, 300).until(
                lambda d: d.find_elements(
                    By.XPATH, "//*[contains(@class,'animate-spin')]"
                )
            )
        except Exception:
            pass  # generation may finish before a spinner is even rendered

        try:
            WebDriverWait(self.driver, 300).until(
                lambda d: not d.find_elements(
                    By.XPATH, "//*[contains(@class,'animate-spin')]"
                )
            )
        except Exception:
            pass  # if no spinner was detected, generation likely finished already

        # Brief pause to let React re-render the "Готово" badge
        _t.sleep(2)

    def wait_for_plan_ready(self, timeout: int = 60):
        """Wait until the 'Поурочный план' card shows a 'Готово' / 'Дайын' badge."""
        import time as _t
        deadline = _t.time() + timeout
        while _t.time() < deadline:
            els = self.driver.find_elements(*self._PLAN_READY_STATUS)
            if els:
                return
            _t.sleep(1)
        raise TimeoutError(
            f"'Готово' badge not found on lesson plan card after {timeout}s"
        )

    def click_edit_lesson_plan(self):
        """Click the 'Редактировать' / 'Өңдеу' button on the lesson plan card."""
        url_before = self.driver.current_url
        edit_btn = self.wait.until(EC.element_to_be_clickable(self._EDIT_PLAN_BTN))
        js_click(self.driver, edit_btn)
        # Wait for navigation to the lesson plan editor page
        self.wait.until(lambda d: d.current_url != url_before)

    # ------------------------------------------------------------------
    def _fill(self, locator, text: str):
        """Fill a React-controlled textarea reliably.

        Steps:
        1. Scroll the textarea into view and click it to focus.
        2. Ctrl+A to select any existing content.
        3. send_keys(text) — real keyboard events that React's synthetic
           system processes, updating state and enabling the submit button.
        """
        el = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", el
        )
        el.click()
        el.send_keys(Keys.CONTROL + "a")
        el.send_keys(text)
