"""
Test: Upload button opens the upload modal.

Checks:
- Clicking 'Загрузить' opens an upload/modal dialog
- The modal can be dismissed
"""

import time

from pages.library.library_page import LibraryPage


def test_upload_modal_opens(driver, wait, base_url, login):
    """Clicking 'Загрузить' should open the upload material modal."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    page.click_upload()
    time.sleep(1)

    # The upload modal title must appear
    page.wait_upload_modal_open()

    # Close it to keep state clean for subsequent tests
    page.close_upload_modal()
    time.sleep(0.5)

    # Confirm modal is gone — toolbar still accessible
    page.find(page._UPLOAD_BTN)
