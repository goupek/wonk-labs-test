"""
Tests: Actions on individual material cards.

Covers:
1. 'Открыть' (Open) — opens a material preview or detail page
2. Edit button — opens the edit material modal/page
3. Download button — triggers a file download (we verify the click doesn't crash)
4. 'Скачать PDF' — triggers PDF download (same approach)
"""

import time

from selenium.webdriver.common.by import By

from pages.library.library_page import LibraryPage


def test_open_first_material(driver, wait, base_url, login):
    """Clicking 'Открыть' on the first card should navigate away from /ru/library."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    page.click_open_first()
    time.sleep(1.5)

    # Should have navigated to a material detail/preview page
    assert "/ru/library" not in driver.current_url or "/ru/library/" in driver.current_url, (
        f"Expected to navigate away from list after opening material, got: {driver.current_url}"
    )

    # Navigate back for subsequent tests
    driver.back()
    page.find(page._UPLOAD_BTN)


def test_edit_first_material(driver, wait, base_url, login):
    """Clicking the edit button should open an edit modal or navigate to edit page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    page.click_edit_first()
    time.sleep(1)

    # Either a modal appeared or we navigated to an edit URL
    # We just verify the browser didn't crash — toolbar or a modal title is present
    edit_indicators = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'Редактировать') or contains(text(),'Изменить') or contains(text(),'Edit')]"
    )
    assert edit_indicators or "/edit" in driver.current_url, (
        "No edit modal or edit page appeared after clicking edit button"
    )

    # Try to get back to a clean state
    try:
        from selenium.webdriver.common.keys import Keys
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
    except Exception:
        pass
    if "/ru/library" not in driver.current_url:
        driver.back()
        page.find(page._UPLOAD_BTN)


def test_download_first_material(driver, wait, base_url, login):
    """Clicking 'Скачать материал' should not crash the page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    page.click_download_first()
    time.sleep(2)  # allow download to initiate

    # Page should still be on /ru/library
    assert "/ru/library" in driver.current_url, (
        f"Unexpected navigation after download click: {driver.current_url}"
    )
    page.find(page._UPLOAD_BTN)


def test_download_pdf_first_material(driver, wait, base_url, login):
    """Clicking 'Скачать PDF' should not crash the page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # PDF button is only on non-image cards — skip if none found
    pdf_btns = driver.find_elements(*page._PDF_BTNS)
    if not pdf_btns:
        return  # no PDF-downloadable cards on current page, skip gracefully

    from utils.helpers import js_click
    js_click(driver, pdf_btns[0])
    time.sleep(2)

    assert "/ru/library" in driver.current_url, (
        f"Unexpected navigation after PDF download click: {driver.current_url}"
    )
    page.find(page._UPLOAD_BTN)
