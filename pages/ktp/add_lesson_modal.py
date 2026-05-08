from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.helpers import js_click

# Slider boundaries in seconds (06:00 – 20:00)
_SLIDER_MIN = 21600
_SLIDER_MAX = 72000


def _hhmm_to_seconds(t: str) -> int:
    """Convert 'HH:MM' to total seconds from midnight."""
    h, m = map(int, t.split(":"))
    return h * 3600 + m * 60


class AddLessonModal(BasePage):
    _TOPIC_INPUT  = (By.ID, "lesson-topic")
    _TODAY_BTN    = (By.XPATH, "//td[@data-today='true']//button")
    _SLIDER_TRACK = (By.XPATH, "//span[@data-slot='slider']")
    _SUBMIT_BTN   = (By.XPATH, "//button[contains(., 'Создать урок')]")

    def wait_open(self):
        self.find(self._TOPIC_INPUT)

    def fill_topic(self, topic: str):
        inp = self.find(self._TOPIC_INPUT)
        inp.clear()
        inp.send_keys(topic)

    def select_today(self):
        # JS click is atomic — avoids StaleElementReferenceException from React re-render.
        self.wait.until(
            lambda d: d.find_elements(By.XPATH, "//td[@data-today='true']//button")
        )
        self.driver.execute_script(
            "document.querySelector('td[data-today=\"true\"] button').click();"
        )

    def set_time(self, start: str, end: str):
        """Drag the range-slider thumbs to the given HH:MM start and end times."""
        self.find(self._SLIDER_TRACK)  # wait for slider to appear
        # Move Maximum first — Minimum can't exceed Maximum, so setting end
        # time first ensures start won't be clamped.
        self._drag_thumb("Maximum", _hhmm_to_seconds(end))
        self._drag_thumb("Minimum", _hhmm_to_seconds(start))

    def submit(self):
        self.click(self._SUBMIT_BTN)
        self.wait_gone(self._SUBMIT_BTN)

    # ------------------------------------------------------------------
    def _drag_thumb(self, label: str, target_seconds: int):
        """Move a slider thumb to the target time (in seconds).

        Reads aria-valuenow for the current value and scales the delta to
        pixels using the track width — no dependency on absolute X coordinates.
        """
        track = self.driver.find_element(*self._SLIDER_TRACK)
        thumb = self.driver.find_element(
            By.XPATH, f"//span[@role='slider'][@aria-label='{label}']"
        )

        current_value = int(thumb.get_attribute("aria-valuenow"))
        track_w = track.rect["width"]

        delta_ratio = (target_seconds - current_value) / (_SLIDER_MAX - _SLIDER_MIN)
        delta_x = int(delta_ratio * track_w)

        ActionChains(self.driver)\
            .click_and_hold(thumb)\
            .move_by_offset(delta_x, 0)\
            .release()\
            .perform()
