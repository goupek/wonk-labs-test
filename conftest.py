import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import BASE_URL, ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD
from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "false").lower() == "true":
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def wait(driver):
    return WebDriverWait(driver, 15)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def login(driver, wait, base_url):
    """Log in once for the entire test session."""
    page = LoginPage(driver, wait, base_url)
    page.open()
    page.login(ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD)


@pytest.fixture(scope="session")
def shared_state():
    """Mutable dict for passing data between tests in the same session."""
    return {}
