"""
Tests: Clicking a lesson plan card opens a preview modal.

Clicking a card does NOT navigate — it opens an inline modal with:
  - The lesson plan title and subject
  - A close (X) button
  - A "Посмотреть план урока" gradient button that navigates to the detail page
"""

from pages.lesson_plans_library.lesson_plans_page import LessonPlansPage


def test_click_card_opens_modal(driver, wait, base_url, login):
    """Clicking the first card should open a preview modal."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    url_before = driver.current_url

    page.click_first_card()

    # Modal must be visible — URL stays the same
    assert driver.current_url == url_before, (
        "URL changed after clicking card — expected modal, not navigation"
    )
    # "Посмотреть план урока" button inside the modal
    page.find(page._MODAL_VIEW_BTN)


def test_close_modal_with_x(driver, wait, base_url, login):
    """The X button inside the modal should close it."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_first_card()
    page.find(page._MODAL_VIEW_BTN)  # confirm modal is open

    page.close_modal()

    # Cards must still be visible after closing
    page.wait_for_cards()
    assert page.count_cards() > 0, "No cards visible after closing modal"


def test_view_lesson_plan_navigates(driver, wait, base_url, login):
    """'Посмотреть план урока' should navigate to the lesson plan detail page."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    page.click_first_card()
    page.click_view_lesson_plan()

    assert "/ru/lesson-plans-library/" in driver.current_url, (
        f"Expected detail page URL after clicking 'Посмотреть план урока', "
        f"got: {driver.current_url}"
    )
    assert driver.current_url.rstrip("/") != f"{base_url}/ru/lesson-plans-library", (
        "Stayed on the list page — navigation did not happen"
    )

    driver.back()
    page.wait_for_cards()
