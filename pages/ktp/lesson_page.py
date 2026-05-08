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

    def click_generate(self):
        self.click(self._GENERATE_BTN)
        # Wait for the first textarea to appear
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

        # Hold the browser open for the full 5 minutes from this point
        deadline = _t.monotonic() + 300
        try:
            WebDriverWait(self.driver, 300).until(
                lambda d: d.find_elements(
                    By.XPATH, "//*[contains(@class,'animate-spin')]"
                )
            )
            WebDriverWait(self.driver, 300).until(
                lambda d: not d.find_elements(
                    By.XPATH, "//*[contains(@class,'animate-spin')]"
                )
            )
        except Exception:
            pass

        remaining = deadline - _t.monotonic()
        if remaining > 0:
            _t.sleep(remaining)

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
