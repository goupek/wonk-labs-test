import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import BASE_URL, ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD
from pages.login_page import LoginPage


def pytest_collection_modifyitems(items):
    """Enforce a deterministic test execution order across the full suite.

    Order within the full run:
      0. auth
      1. chatbot/navigate_chatbot  – just visits the page
      2. chatbot/suggestion_cards  – needs fresh chatbot (suggestion cards visible)
      3. chatbot/send_message      – sends messages, dirties chatbot state
      4. chatbot/conversation      – sends more messages, leaves chatbot dirty
      5. ktp/*                     – create_ktp → create_lesson → generate_lesson_plan
                                     (sequential; each step depends on the previous)
      6. lesson_plans_library, library  – independent of ktp shared_state
      7. presentations/*           – depends on ktp shared_state (ktp_name, lesson_topic)
    """
    def sort_key(item):
        nid = item.nodeid.replace("\\", "/")
        # Desired execution order:
        #   0  auth
        #   1  chatbot/navigate_chatbot  – just visits, no messages
        #   2  chatbot/suggestion_cards  – needs fresh chatbot
        #   3  chatbot/send_message      – sends messages, dirties state
        #   4  chatbot/conversation      – sends more messages
        #   5  ktp/*                     – create_ktp → create_lesson → generate
        #   6  lesson_plans_library, library  – independent
        #   7  presentations/*           – depends on ktp shared_state
        if "auth/" in nid:
            return 0
        if "chatbot/navigate_chatbot" in nid:
            return 1
        if "chatbot/suggestion_cards" in nid:
            return 2
        if "chatbot/send_message" in nid:
            return 3
        if "chatbot/conversation" in nid:
            return 4
        if "ktp/" in nid:
            return 5
        if "presentations/" in nid:
            return 7
        return 6  # lesson_plans_library, library

    # Python's list.sort() is stable, so relative order within each
    # group is preserved from pytest's original collection order.
    items.sort(key=sort_key)


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
