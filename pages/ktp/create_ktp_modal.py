from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.helpers import js_click


class CreateKtpModal(BasePage):
    _TITLE = (By.XPATH, "//*[normalize-space(text())='Создать КТП']")
    _NAME_INPUT = (By.ID, "ktp-topic")
    _SUBJECT_TRIGGER = (By.XPATH, "//button[@role='combobox'][.//*[normalize-space(text())='Выберите предмет']]")
    _CLASS_TRIGGER = (By.XPATH, "//button[@role='combobox'][.//*[normalize-space(text())='Выберите класс']]")
    _QUARTER_TRIGGER = (By.XPATH, "//button[@role='combobox'][.//*[contains(text(),'четверть')]]")
    _SUBMIT_BTN = (By.XPATH, "//button[@type='submit' and normalize-space(text())='Создать']")

    def wait_open(self):
        self.find(self._TITLE)

    def fill_name(self, name: str):
        inp = self.find(self._NAME_INPUT)
        inp.clear()
        inp.send_keys(name)

    def select_subject(self, subject: str):
        self._radix_select(self._SUBJECT_TRIGGER, subject)

    def select_grade(self, grade: str):
        self._radix_select(self._CLASS_TRIGGER, grade)

    def select_quarter(self, quarter: str):
        self._radix_select(self._QUARTER_TRIGGER, quarter)

    def submit(self):
        self.click(self._SUBMIT_BTN)
        self.wait_gone(self._TITLE)

    # ------------------------------------------------------------------
    def _radix_select(self, trigger_locator, option_text: str):
        """Click a Radix UI select trigger and choose an option by visible text."""
        self.click(trigger_locator)
        option = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//*[@role='option'][.//*[normalize-space(text())='{option_text}']]")
            )
        )
        js_click(self.driver, option)
