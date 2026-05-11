"""
Tests: Clicking a lesson plan card opens its detail page.

The entire card is a <div role="button"> — clicking anywhere on it navigates
to /ru/lesson-plans-library/{id}.
"""

import time

from pages.lesson_plans_library.lesson_plans_page import LessonPlansPage


def test_click_first_card_opens_detail(driver, wait, base_url, login):
    """Clicking the first card should navigate to its detail page."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    titles = page.get_card_titles()
    assert titles, "No cards found to click"

    page.click_first_card()

    assert "/ru/lesson-plans-library/" in driver.current_url, (
        f"Expected detail page URL, got: {driver.current_url}"
    )
    # URL must be different from the list page (has an ID after the path)
    assert driver.current_url.rstrip("/") != f"{base_url}/ru/lesson-plans-library", (
        "Stayed on the list page after clicking a card"
    )

    driver.back()
    page.wait_for_cards()


def test_back_navigation_returns_to_list(driver, wait, base_url, login):
    """After opening a card detail, browser back should return to the list."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_first_card()
    time.sleep(0.5)

    driver.back()
    time.sleep(1)

    assert "/ru/lesson-plans-library" in driver.current_url, (
        f"Expected to return to list page, got: {driver.current_url}"
    )
    page.wait_for_cards()
    assert page.count_cards() > 0, "No cards visible after going back"
