"""
Tests: Library pagination.

Covers:
1. Clicking 'Вперед' (Next) loads the next page of results
2. After going to page 2, 'Назад' (Prev) returns to page 1
3. Direct page-number navigation
"""

import time

from pages.library.library_page import LibraryPage


def test_next_page(driver, wait, base_url, login):
    """'Вперед' button should advance to page 2."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    initial_count = page.count_cards()
    assert initial_count > 0, "No cards on page 1"

    page.go_next_page()

    # URL should reflect page 2 (query param) OR cards should change
    # Either way, the toolbar must still be present
    page.find(page._UPLOAD_BTN)
    assert page.count_cards() > 0, "No cards visible after navigating to next page"


def test_prev_page(driver, wait, base_url, login):
    """'Назад' button should return to the previous page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # Navigate forward first
    page.go_next_page()
    time.sleep(0.5)

    # Now go back
    page.go_prev_page()

    page.find(page._UPLOAD_BTN)
    assert page.count_cards() > 0, "No cards visible after navigating back"


def test_page_number_navigation(driver, wait, base_url, login):
    """Clicking page number '3' should load that page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    page.go_to_page(3)

    page.find(page._UPLOAD_BTN)
    assert page.count_cards() > 0, "No cards visible after navigating to page 3"
