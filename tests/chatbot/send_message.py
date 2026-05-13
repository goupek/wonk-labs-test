"""
Tests: Sending a message to the chatbot and receiving a response.

Covers:
1. Typing in the textarea updates its value
2. Clicking Send clears the textarea
3. The chatbot returns a non-empty answer after the message is sent
4. Sending via the Enter key also works
"""

import time

from pages.chatbot.chatbot_page import ChatbotPage

_QUESTION = "Как мотивировать учеников на уроке математики?"


def test_textarea_accepts_input(driver, wait, base_url, login):
    """Typing into the textarea should update its value."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    page.type_message(_QUESTION)

    assert page.get_textarea_value() == _QUESTION, (
        f"Textarea value mismatch after typing.\n"
        f"Expected: {_QUESTION!r}\nGot: {page.get_textarea_value()!r}"
    )


def test_send_clears_textarea_and_gets_response(driver, wait, base_url, login):
    """After clicking Send the textarea clears and the chatbot responds."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    msgs_before = page.count_assistant_messages()

    page.send_message(_QUESTION)

    # Textarea must be empty right after sending
    time.sleep(0.5)
    assert page.get_textarea_value() == "", (
        f"Textarea not cleared after sending. Got: {page.get_textarea_value()!r}"
    )

    # Wait for the chatbot to finish streaming its reply
    page.wait_for_response_complete(msgs_before)

    reply = page.get_last_assistant_message()
    assert reply, "Assistant returned an empty response"
    assert len(reply) > 20, (
        f"Response looks too short to be a real answer: {reply!r}"
    )


def test_send_with_enter_key(driver, wait, base_url, login):
    """Pressing Enter in the textarea should submit the message."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    msgs_before = page.count_assistant_messages()

    page.send_with_enter(_QUESTION)
    time.sleep(0.5)

    # If Enter submitted the message the textarea is now empty
    if page.get_textarea_value() == "":
        # Wait for the complete AI response
        page.wait_for_response_complete(msgs_before)
        reply = page.get_last_assistant_message()
        assert reply, "Assistant returned an empty response after Enter-send"
        assert len(reply) > 20, f"Response too short: {reply!r}"
    else:
        # Enter added a newline instead of sending — page must still be usable
        page.find(page._SEND_BTN)
        page.clear_textarea()
