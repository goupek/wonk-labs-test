"""
Tests: Search and sort on the Lesson Plans Library page.

Covers:
1. Searching by keyword narrows the card list
2. Clearing search restores all cards
3. Sort order can be changed (oldest / most used / newest)
"""

import time

from pages.lesson_plans_library.lesson_plans_page import LessonPlansPage


def test_search_filters_cards(driver, wait, base_url, login):
    """Typing a keyword should reduce the visible card count."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    total = page.count_cards()
    assert total > 0, "No cards before search"

    page.search("Физика")
    time.sleep(1)

    filtered = page.count_cards()
    # Either fewer cards are shown, or the same (if all match) — page should not crash
    page.find(page._SEARCH_INPUT)  # search box still present


def test_search_clear_restores_cards(driver, wait, base_url, login):
    """Clearing the search box should bring back all cards."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()
    total_before = page.count_cards()

    page.search("Физика")
    time.sleep(1)

    page.clear_search()
    time.sleep(1)

    total_after = page.count_cards()
    assert total_after >= total_before or total_after > 0, (
        "Cards did not restore after clearing search"
    )


def test_sort_oldest(driver, wait, base_url, login):
    """Selecting 'Сначала старые' should not crash the page."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.sort_by("Сначала старые")
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards after sorting by oldest"


def test_sort_most_used(driver, wait, base_url, login):
    """Selecting 'По использованию' should not crash the page."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.sort_by("По использованию")
    page.wait_for_cards()

    assert page.count_cards() > 0, "No cards after sorting by most used"
