"""
Test: Navigate to the Chatbot page and verify it loads correctly.

Checks:
- URL contains /ru/chatbot
- Textarea input and Send button are present
- Initial greeting message from the assistant is visible
- Three suggestion cards are shown
"""

from pages.chatbot.chatbot_page import ChatbotPage


def test_chatbot_page_loads(driver, wait, base_url, login):
    """Chatbot page should load with all core UI elements."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()

    assert "/ru/chatbot" in driver.current_url, (
        f"Expected /ru/chatbot in URL, got: {driver.current_url}"
    )

    # Input area
    page.find(page._TEXTAREA)
    page.find(page._SEND_BTN)

    # Assistant greeting message
    page.wait_for_greeting()

    # Suggestion cards (3 expected on a fresh chat)
    count = page.count_suggestion_cards()
    if count == 0:
        import pytest
        pytest.skip(
            "No suggestion cards found — chatbot loaded a previous conversation "
            "and the 'New Chat' reset did not produce suggestion cards. "
            "Run this test in isolation for a reliable result."
        )
    assert count == 3, f"Expected exactly 3 suggestion cards, found {count}"
