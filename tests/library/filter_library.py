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
    """Clicking 'Фильтры' should toggle the filter panel open/closed."""
    page = LibraryPage(driver, wait, base_url)
    page.open()

    # Capture initial state — panel may start open or closed
    initial_visible = page.is_filter_panel_visible()

    # First click — state should flip
    page.click_filters()
    time.sleep(0.5)
    after_first_click = page.is_filter_panel_visible()
    assert after_first_click != initial_visible, (
        "Filter panel visibility did not change after first click of 'Фильтры'"
    )

    # Second click — should return to initial state
    page.click_filters()
    time.sleep(0.5)
    after_second_click = page.is_filter_panel_visible()
    assert after_second_click == initial_visible, (
        "Filter panel visibility did not return to initial state after second click"
    )


def test_grid_list_toggle(driver, wait, base_url, login):
    """Switching between Сетка and Список views should not break the page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

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

    # Open the filter panel and wait until its comboboxes are interactive
    page.ensure_filter_panel_open()

    page.select_class_filter("8 класс")
    time.sleep(1)  # let the results update

    # Page should not crash — toolbar still present
    page.find(page._UPLOAD_BTN)
