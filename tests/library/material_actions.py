"""
Tests: Actions on individual material cards.

Covers:
1. 'Открыть' (Open) — opens a material preview modal
2. Edit button — opens the edit material modal/page
3. Download button — triggers a file download (stays on /ru/library)
4. 'Скачать PDF' — triggers PDF download (same approach)
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.library.library_page import LibraryPage


def test_open_first_material(driver, wait, base_url, login):
    """Clicking 'Открыть' should open a preview modal on the same page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_open_first()
    time.sleep(1)

    # Открыть opens an inline modal/drawer, not a new page.
    # Verify the modal appeared — a dialog role or close button should be present.
    modal_present = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[@role='dialog'] | //button[@aria-label='Close']"
                       " | //*[contains(@class,'sheet')] | //*[contains(@class,'drawer')]")
        )
    )
    assert modal_present, "No preview modal appeared after clicking 'Открыть'"

    # Close the modal to restore clean state
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    time.sleep(0.5)


def test_edit_first_material(driver, wait, base_url, login):
    """Clicking the edit button should open an edit modal or navigate to edit page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_edit_first()
    time.sleep(1)

    edit_indicators = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'Редактировать') or contains(text(),'Изменить')]"
        " | //*[@role='dialog']"
    )
    assert edit_indicators or "/edit" in driver.current_url, (
        "No edit modal or edit page appeared after clicking edit button"
    )

    # Return to a clean state
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    time.sleep(0.3)
    if "/ru/library" not in driver.current_url:
        driver.back()
        page.find(page._UPLOAD_BTN)


def test_download_first_material(driver, wait, base_url, login):
    """Clicking 'Скачать материал' should not crash the page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_download_first()
    time.sleep(2)  # allow download to initiate

    assert "/ru/library" in driver.current_url, (
        f"Unexpected navigation after download click: {driver.current_url}"
    )
    page.find(page._UPLOAD_BTN)


def test_download_pdf_first_material(driver, wait, base_url, login):
    """Clicking 'Скачать PDF' should not crash the page."""
    from utils.helpers import js_click

    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    pdf_btns = driver.find_elements(*page._PDF_BTNS)
    if not pdf_btns:
        return  # no PDF-downloadable cards on this page, skip gracefully

    js_click(driver, pdf_btns[0])
    time.sleep(2)

    assert "/ru/library" in driver.current_url, (
        f"Unexpected navigation after PDF download click: {driver.current_url}"
    )
    page.find(page._UPLOAD_BTN)
