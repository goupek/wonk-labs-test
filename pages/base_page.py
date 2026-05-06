from selenium.webdriver.support import expected_conditions as EC

from utils.helpers import js_click


class BasePage:
    def __init__(self, driver, wait, base_url):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url

    def go_to(self, path: str):
        """Navigate to a path relative to base_url (e.g. '/en/some-section')."""
        self.driver.get(f"{self.base_url}{path}")
        self.wait.until(lambda d: path in d.current_url)

    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        js_click(self.driver, el)
        return el

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, by, xpath):
        return self.driver.find_elements(by, xpath)

    def wait_gone(self, locator):
        self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_url(self, fragment):
        self.wait.until(EC.url_contains(fragment))
