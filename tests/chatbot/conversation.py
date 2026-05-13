"""
Tests: Multi-turn conversation with the chatbot.

Each test sends a distinct pedagogical question, waits for the full
streamed response, then verifies the reply is substantive before
(optionally) sending the next question.

Questions are chosen from different teaching-methodology domains so
the answers should genuinely differ.
"""

from pages.chatbot.chatbot_page import ChatbotPage

# Three distinct questions covering different teaching domains
_Q1 = "Как сделать урок более интерактивным для учеников 6 класса?"
_Q2 = "Какие приёмы помогут удержать внимание учеников в середине урока?"
_Q3 = "Как правильно давать обратную связь ученикам после контрольной работы?"


def _assert_reply(reply: str, label: str):
    """Helper: the reply must be a real, non-trivial answer."""
    assert reply, f"[{label}] Assistant returned an empty reply"
    assert len(reply) > 30, (
        f"[{label}] Reply looks too short ({len(reply)} chars): {reply!r}"
    )


def test_ask_interactive_lesson_question(driver, wait, base_url, login):
    """Send question 1 (interactive lessons) and wait for a full response."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    before = page.count_assistant_messages()
    page.send_message(_Q1)

    page.wait_for_response_complete(before)
    _assert_reply(page.get_last_assistant_message(), "Q1")


def test_ask_attention_keeping_question(driver, wait, base_url, login):
    """Send question 2 (attention techniques) and wait for a full response."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    before = page.count_assistant_messages()
    page.send_message(_Q2)

    page.wait_for_response_complete(before)
    _assert_reply(page.get_last_assistant_message(), "Q2")


def test_ask_feedback_question(driver, wait, base_url, login):
    """Send question 3 (giving feedback) and wait for a full response."""
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    before = page.count_assistant_messages()
    page.send_message(_Q3)

    page.wait_for_response_complete(before)
    _assert_reply(page.get_last_assistant_message(), "Q3")


def test_multi_turn_conversation(driver, wait, base_url, login):
    """Send three questions back-to-back in the same chat session.

    After each send the test waits for the bot to finish streaming before
    asking the next question, ensuring the conversation remains coherent.
    """
    page = ChatbotPage(driver, wait, base_url)
    page.open()
    page.wait_for_greeting()

    for i, question in enumerate((_Q1, _Q2, _Q3), start=1):
        before = page.count_assistant_messages()

        page.send_message(question)

        # Wait for the streaming response to finish
        page.wait_for_response_complete(before)

        reply = page.get_last_assistant_message()
        _assert_reply(reply, f"turn {i}")

        # Textarea must be clear before the next turn
        assert page.get_textarea_value() == "", (
            f"Textarea was not cleared after turn {i}"
        )
