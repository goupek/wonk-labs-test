
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
    """'Посмотреть план урока' should navigate away from the list page."""
    page = LessonPlansPage(driver, wait, base_url)
    page.open()
    page.wait_for_cards()

    url_before = driver.current_url
    page.click_first_card()
    page.click_view_lesson_plan()

    # URL must change — detail page may live at /ru/lesson-plan-editor/<id>, etc.
    assert driver.current_url != url_before, (
        f"URL did not change after clicking 'Посмотреть план урока'; "
        f"still at: {driver.current_url}"
    )
    assert driver.current_url.rstrip("/") != f"{base_url}/ru/lesson-plans-library", (
        "Stayed on the list page — navigation did not happen"
    )
""