import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.helpers import js_click


class ChatbotPage(BasePage):
    # ── Chat input ─────────────────────────────────────────────────────────
    _TEXTAREA = (By.XPATH, "//textarea[contains(@placeholder,'Задайте вопрос')]")
    _SEND_BTN = (By.XPATH, "//button[@type='submit']")

    # ── Assistant message bubbles ──────────────────────────────────────────
    # The greeting (and every subsequent assistant reply) has rounded-tl-none
    _ASST_BUBBLE = (By.XPATH,
        "//div[contains(@class,'rounded-2xl') and contains(@class,'rounded-tl-none')]")

    # ── Suggestion cards ───────────────────────────────────────────────────
    _CARDS = (By.XPATH,
        "//div[contains(@class,'cursor-pointer') and contains(@class,'rounded-[14px]')]")

    # ── "New chat" button (shown when a previous conversation is loaded) ───
    # Try common label patterns in Russian and English
    _NEW_CHAT_BTN = (By.XPATH,
        "//button[contains(normalize-space(.),'Новый чат')"
        "       or contains(normalize-space(.),'New chat')"
        "       or contains(normalize-space(.),'Новая беседа')]"
        " | //*[@aria-label='Новый чат' or @aria-label='New chat'"
        "        or @aria-label='Новая беседа']")

    def open(self):
        """Navigate to the chatbot and ensure the initial greeting state.

        Strategy (in order):
        1. Navigate to /ru/chatbot.
        2. If suggestion cards are visible → done (fresh chat).
        3. Try clicking a "New Chat" button (Russian or English label).
        4. Fallback: clear localStorage (conversation history lives there)
           and reload — this reliably resets to the initial state without
           logging the user out (auth uses HTTP-only cookies, not localStorage).
        """
        self.go_to("/ru/chatbot")
        time.sleep(1)

        if not self.driver.find_elements(*self._CARDS):
            self._start_new_chat()

    def _start_new_chat(self):
        """Reset the chatbot to its initial (greeting + cards) state."""
        # Try known "New Chat" button labels first
        btns = self.driver.find_elements(*self._NEW_CHAT_BTN)
        if btns:
            js_click(self.driver, btns[0])
            time.sleep(1.5)
            if self.driver.find_elements(*self._CARDS):
                return  # success

        # Fallback: remove only chat-related localStorage keys, preserving
        # auth tokens and app-level state that other pages rely on.
        self.driver.execute_script("""
            var toRemove = [];
            for (var i = 0; i < localStorage.length; i++) {
                var k = localStorage.key(i);
                if (/chat|conversation|message|history|thread/i.test(k)) {
                    toRemove.push(k);
                }
            }
            toRemove.forEach(function(k) { localStorage.removeItem(k); });
        """)
        self.driver.refresh()
        time.sleep(2)

    # ── Textarea helpers ───────────────────────────────────────────────────

    def type_message(self, text: str):
        """Scroll the textarea into view, focus it via JS, then type."""
        inp = self.wait.until(EC.element_to_be_clickable(self._TEXTAREA))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", inp
        )
        js_click(self.driver, inp)
        inp.send_keys(text)
        # Give React a beat to process the input event and enable the send button
        time.sleep(0.4)

    def get_textarea_value(self) -> str:
        """Return the current content of the chat textarea."""
        inp = self.find(self._TEXTAREA)
        return inp.get_attribute("value") or ""

    def clear_textarea(self):
        """Clear the textarea via keyboard."""
        inp = self.wait.until(EC.element_to_be_clickable(self._TEXTAREA))
        js_click(self.driver, inp)
        inp.send_keys(Keys.CONTROL + "a")
        inp.send_keys(Keys.DELETE)
        time.sleep(0.2)

    # ── Send helpers ───────────────────────────────────────────────────────

    def click_send(self):
        """Click the gradient Send button.

        The button is `disabled` until React processes the textarea input,
        so we poll for it to become enabled instead of using the standard
        element_to_be_clickable check (which won't ignore the disabled attr).
        """
        def _enabled_btn(d):
            try:
                btn = d.find_element(*self._SEND_BTN)
                if btn.get_attribute("disabled"):
                    return False
                if btn.get_attribute("aria-disabled") == "true":
                    return False
                return btn
            except Exception:
                return False

        btn = self.wait.until(_enabled_btn)
        js_click(self.driver, btn)

    def send_message(self, text: str):
        """Type *text* and click the Send button."""
        self.type_message(text)
        self.click_send()
        time.sleep(0.3)

    def send_with_enter(self, text: str):
        """Type *text* and press Enter (React chat shortcut)."""
        inp = self.wait.until(EC.element_to_be_clickable(self._TEXTAREA))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", inp
        )
        js_click(self.driver, inp)
        inp.send_keys(text)
        inp.send_keys(Keys.RETURN)
        time.sleep(0.3)

    # ── Suggestion cards ───────────────────────────────────────────────────

    def count_suggestion_cards(self) -> int:
        return len(self.driver.find_elements(*self._CARDS))

    def get_card_labels(self) -> list[str]:
        """Return the category label from each suggestion card.

        The label is the short badge text (e.g. 'Методика') that sits above
        the question text.  We try several element types because the UI may
        use span, div, or p for the badge depending on the version.
        """
        labels = []
        for card in self.driver.find_elements(*self._CARDS):
            try:
                # Collect all direct-child inline elements and pick the
                # shortest non-empty one that is NOT the main question <p>
                candidates = []
                for tag in ("span", "div", "p", "small"):
                    for el in card.find_elements(By.TAG_NAME, tag):
                        txt = el.text.strip()
                        if txt:
                            candidates.append(txt)

                if not candidates:
                    continue

                # The label is always shorter than the question — pick the
                # shortest text that is ≤ 30 chars (question texts are longer)
                short = [t for t in candidates if len(t) <= 30]
                if short:
                    labels.append(min(short, key=len))
            except Exception:
                pass
        return labels

    def get_card_questions(self) -> list[str]:
        questions = []
        for card in self.driver.find_elements(*self._CARDS):
            try:
                p = card.find_element(By.TAG_NAME, "p")
                txt = p.text.strip()
                if txt:
                    questions.append(txt)
            except Exception:
                pass
        return questions

    def click_suggestion_card(self, index: int = 0):
        """Click the suggestion card at *index* (0 = first).

        Re-fetches the element list on each attempt to survive React
        re-renders that would otherwise cause StaleElementReferenceException.
        """
        from selenium.common.exceptions import StaleElementReferenceException
        for attempt in range(3):
            try:
                cards = self.wait.until(
                    EC.presence_of_all_elements_located(self._CARDS)
                )
                js_click(self.driver, cards[index])
                time.sleep(0.5)
                return
            except StaleElementReferenceException:
                time.sleep(0.3)
        raise RuntimeError(
            f"Could not click suggestion card {index} after 3 attempts (stale)"
        )

    # ── Response helpers ───────────────────────────────────────────────────

    def wait_for_greeting(self):
        """Block until the initial assistant greeting bubble is visible."""
        self.find(self._ASST_BUBBLE)

    def count_assistant_messages(self) -> int:
        return len(self.driver.find_elements(*self._ASST_BUBBLE))

    def get_last_assistant_message(self) -> str:
        """Return the text of the most recent assistant bubble."""
        bubbles = self.driver.find_elements(*self._ASST_BUBBLE)
        return bubbles[-1].text.strip() if bubbles else ""

    def wait_for_response_complete(self, msgs_before: int, timeout: int = 60):
        """Send a message then block until the assistant finishes streaming.

        Phase 1 – wait for a new bubble to appear (LLM latency).
        Phase 2 – poll until that bubble's text has been stable for 1.5 s,
                  which signals streaming has finished.

        *msgs_before* must be captured with count_assistant_messages()
        immediately BEFORE the send action.
        """
        slow_wait = WebDriverWait(self.driver, timeout)

        # Phase 1: a new bubble must appear
        slow_wait.until(
            lambda d: len(d.find_elements(*self._ASST_BUBBLE)) > msgs_before
        )

        # Phase 2: text stabilises (streaming complete)
        last_text = None
        stable_since = None
        deadline = time.time() + timeout

        while time.time() < deadline:
            bubbles = self.driver.find_elements(*self._ASST_BUBBLE)
            current_text = bubbles[-1].text if bubbles else ""

            if current_text != last_text:
                last_text = current_text
                stable_since = time.time()
            elif stable_since is not None and current_text:
                if time.time() - stable_since >= 1.5:
                    break   # text unchanged for 1.5 s → streaming done

            time.sleep(0.3)
