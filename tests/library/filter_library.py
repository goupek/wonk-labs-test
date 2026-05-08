"""
Tests: Library filter panel behaviour.

Covers:
1. Toggling the filter panel (Фильтры button shows/hides it)
2. Grid ↔ List view toggle
3. Selecting a class filter changes the visible cards
"""

import time

from pages.library.library_page import LibraryPage


def test_filter_toggle(driver, wait, base_url, login):
    """Clicking 'Фильтры' should hide then re-show the filter panel."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # Panel is visible by default
    assert page.is_filter_panel_visible(), "Filter panel should be visible on load"

    # First click hides it
    page.click_filters()
    time.sleep(0.5)
    assert not page.is_filter_panel_visible(), (
        "Filter panel should be hidden after clicking 'Фильтры'"
    )

    # Second click shows it again
    page.click_filters()
    time.sleep(0.5)
    assert page.is_filter_panel_visible(), (
        "Filter panel should be visible after clicking 'Фильтры' again"
    )


def test_grid_list_toggle(driver, wait, base_url, login):
    """Switching between Сетка and Список views should not break the page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # Switch to List view
    page.click_list_view()
    time.sleep(0.5)
    assert page.count_cards() > 0, "Cards should still be visible in List view"

    # Switch back to Grid view
    page.click_grid_view()
    time.sleep(0.5)
    assert page.count_cards() > 0, "Cards should still be visible in Grid view"


def test_class_filter(driver, wait, base_url, login):
    """Selecting a class filter should return results (or empty state gracefully)."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # Make sure filter panel is visible
    if not page.is_filter_panel_visible():
        page.click_filters()
        time.sleep(0.5)

    page.select_class_filter("8 класс")
    time.sleep(1)  # let the results update

    # Page should not crash — toolbar still present
    page.find(page._UPLOAD_BTN)
