"""
Test: Navigate to the Lesson Plans Library and verify it loads correctly.

Checks:
- URL contains /ru/lesson-plans-library
- Search input, Фильтры button, and sort select are present
- At least one lesson plan card is visible after data loads
"""

from pages.lesson_plans_library.lesson_plans_page import LessonPlansPage


def test_lesson_plans_page_loads(driver, wait, base_url, login):
    page = LessonPlansPage(driver, wait, base_url)
    page.open()

    assert "/ru/lesson-plans-library" in driver.current_url, (
        f"Expected /ru/lesson-plans-library in URL, got: {driver.current_url}"
    )

    page.find(page._SEARCH_INPUT)
    page.find(page._FILTER_BTN)
    page.find(page._SORT_SELECT)

    page.wait_for_cards()
    assert page.count_cards() > 0, "No lesson plan cards found on the page"
