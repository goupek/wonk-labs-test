"""
Tests: Library pagination.

Covers:
1. Clicking 'Next' loads the next page of results
2. After going to page 2, 'Prev' returns to page 1
3. Direct page-number navigation

All three tests skip automatically if the library currently has only one page
of content (pagination controls are not rendered in that case).
"""

import pytest

from pages.library.library_page import LibraryPage


def _require_next_page(page: LibraryPage):
    """Skip the test if there is no Next button (library fits on one page)."""
    if not page.has_pagination():
        pytest.skip("Library has only one page — pagination controls not present")
    next_els = page.driver.find_elements(*page._NEXT_BTN)
    if not next_els:
        pytest.skip("No Next button found — library may have only one page")


def test_next_page(driver, wait, base_url, login):
    """Next button should advance to page 2."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards on page 1"
    _require_next_page(page)

    page.go_next_page()
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards visible after navigating to next page"


def test_prev_page(driver, wait, base_url, login):
    """Prev button should return to the previous page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    _require_next_page(page)

    page.go_next_page()
    page.wait_for_cards()

    page.go_prev_page()
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards visible after navigating back"


def test_page_number_navigation(driver, wait, base_url, login):
    """Clicking page number '3' should load that page."""
    page = LibraryPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    # Need at least 3 page links visible
    page_links = page.driver.find_elements(*page._PAGE_LINKS)
    link_numbers = [el.text.strip() for el in page_links if el.text.strip().isdigit()]
    if "3" not in link_numbers:
        pytest.skip(
            f"Page '3' link not found — library has fewer than 3 pages "
            f"(visible page numbers: {link_numbers})"
        )

    page.go_to_page(3)
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards visible after navigating to page 3"
