import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from utils.config import BASE_URL, ACCOUNT_1_USERNAME, ACCOUNT_1_PASSWORD
from pages.login_page import LoginPage


def pytest_collection_modifyitems(items):
    """Move chatbot/conversation tests to run after all other chatbot tests.

    Conversation tests send multiple messages and leave the chatbot in a
    'dirty' state (existing conversation loaded, no suggestion cards).
    Running them last ensures navigate/send/suggestion-card tests always
    see a fresh chatbot session.

    Order within the full run:
      1. auth
      2. chatbot/navigate_chatbot, send_message, suggestion_cards   ← fresh state
      3. chatbot/conversation                                        ← dirties state
      4. ktp, lesson_plans_library, library                         ← unaffected
    """
    def sort_key(item):
        nid = item.nodeid.replace("\\", "/")
        # Desired execution order within chatbot tests:
        #   navigate_chatbot  → just visits the page, doesn't send messages
        #   suggestion_cards  → needs fresh chatbot (suggestion cards visible)
        #   send_message      → sends messages → dirties chatbot state
        #   conversation      → sends more messages, leaves chatbot dirty
        #
        # Everything else (auth, ktp, library) is independent and runs after.
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
        return 5  # ktp, lesson_plans_library, library

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
