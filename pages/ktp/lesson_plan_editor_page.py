import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class LessonPlanEditorPage(BasePage):
    """Page object for the lesson plan (KSP) rich-text editor.

    The editor is a Tiptap / ProseMirror document rendered as one or more
    contenteditable elements.  After AI generation the editor should be
    populated with content — if all editable regions are empty the
    generation has failed silently.
    """

    # Tiptap renders the editable area as div[contenteditable].
    # The attribute value may be the string "true" or just present without a value.
    _EDITORS = (By.XPATH,
        "//div[@contenteditable='true' or @contenteditable='']"
        " | //div[@contenteditable]")

    def wait_for_editor(self, timeout: int = 20):
        """Block until at least one contenteditable region appears on the page."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self._EDITORS)
        )

    def get_editor_texts(self) -> list[str]:
        """Wait for the editor to load, then return the text of every
        contenteditable region (stripped, non-empty entries only)."""
        try:
            self.wait_for_editor()
        except Exception:
            pass  # will return [] below if nothing found

        editors = self.driver.find_elements(*self._EDITORS)
        return [e.text.strip() for e in editors]

    def get_full_page_text(self) -> str:
        """Fallback: return all visible text on the page (for diagnostics)."""
        return self.driver.find_element(By.TAG_NAME, "body").text.strip()

    def is_content_empty(self) -> bool:
        """Return True only if every editable region contains no text."""
        texts = self.get_editor_texts()
        return not any(texts)
