from pages.login_page import LoginPage
from utils.config import ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD


def test_login(driver, wait, base_url):
    page = LoginPage(driver, wait, base_url)
    page.open()
    page.login(ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD)

    assert "/ru/auth" not in driver.current_url, (
        f"Login failed — still on auth page: {driver.current_url}"
    )
