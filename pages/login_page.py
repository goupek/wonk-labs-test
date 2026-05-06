from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils.helpers import js_click


class LoginPage:
    def __init__(self, driver, wait, base_url):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url

    def open(self):
        self.driver.get(f"{self.base_url}/en/sign-in")

    def login(self, email, password):
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)

        password_input = self.driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(password)

        login_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        js_click(self.driver, login_btn)
        self.wait.until(EC.url_contains("/en/"))
