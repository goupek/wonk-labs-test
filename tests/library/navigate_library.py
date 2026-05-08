"""
Test: Navigate to the Library page and verify it loads correctly.

Checks:
- URL contains /ru/library
- Toolbar buttons are present (Фильтры, Сетка, Список, Загрузить)
- At least one material card is visible after the async data loads
"""

from pages.library.library_page import LibraryPage


def test_library_page_loads(driver, wait, base_url, login):
    page = LibraryPage(driver, wait, base_url)
    page.open()

    assert "/ru/library" in driver.current_url, (
        f"Expected /ru/library in URL, got: {driver.current_url}"
    )

    # Toolbar buttons must be present
    page.find(page._FILTER_BTN)
    page.find(page._GRID_BTN)
    page.find(page._LIST_BTN)
    page.find(page._UPLOAD_BTN)

    # Wait for the async card data to arrive, then count
    page.wait_for_cards()
    count = page.count_cards()
    assert count > 0, "No material cards found on the Library page"
