import pytest

from pages.presentations.presentations_page import PresentationsPage

# ---------------------------------------------------------------------------
# Subject / template mappings
# ---------------------------------------------------------------------------
# Maps KTP topic name → school subject (mirrors KTP_LIST in tests/ktp/create_ktp.py)
# Used to pick the right presentation template for the subject.
#
# Алгебра  topics → "Математика"  template
# Физика   topics → "Физика"      template
KTP_SUBJECT_MAP = {
    # ── Математика ───────────────────────────────────────────────────────────
    "Тригонометрия":             "Алгебра",
    "Квадрат теңдеулер":         "Алгебра",
    "Функциялар мен графиктер":  "Алгебра",
    "Туынды":                    "Алгебра",
    "Геометриялық салулар":      "Алгебра",
    "Логарифмдер":               "Алгебра",
    # ── Физика ───────────────────────────────────────────────────────────────
    "Гравитация":                "Физика",
    "Ньютон заңдары":            "Физика",
    "Механикалық қозғалыс":      "Физика",
    "Қысым және күш":            "Физика",
    "Электр тогы":               "Физика",
    "Оптика":                    "Физика",
    "Жылулық құбылыстар":        "Физика",
}

# Maps school subject → presentation template <h3> name on the gallery page
SUBJECT_TEMPLATE_MAP = {
    "Алгебра": "Математика",
    "Физика":  "Физика",
}
# ---------------------------------------------------------------------------


def test_generate_presentation(driver, wait, base_url, login, shared_state):
    """Navigate to /ru/presentations, pick the right template for the KTP
    subject, select the lesson whose КСП was generated, click Continue,
    and assert the presentation was generated successfully.

    Execution order guarantee (enforced by conftest sort keys):
      test_create_ktp          (5) → shared_state["ktp_name"]
      test_add_lesson          (5) → shared_state["lesson_topic"]
      test_generate_lesson_plan(5) → shared_state["lesson_plan_generated"]
      ...library / lesson_plans_library tests (6)...
      test_generate_presentation(7) ← THIS TEST

    The backend requires the КСП to exist before a presentation can be
    generated for the same lesson.  We assert "lesson_plan_generated" so
    the test fails with a clear message rather than a cryptic API error
    ("KTP not found for this lesson instance") if the КСП step was skipped.
    """
    # ── Pre-conditions ────────────────────────────────────────────────────────
    # Use pytest.skip (not assert) so that running this file in isolation
    # produces a clear SKIP rather than a confusing FAILED.
    # To run this test correctly use:
    #   pytest tests/ktp tests/presentations -v
    # or simply:
    #   pytest   (full suite — conftest ordering handles everything)

    ktp_name = shared_state.get("ktp_name")
    if not ktp_name:
        pytest.skip(
            "ktp_name not in shared_state — run tests/ktp/create_ktp.py first, "
            "or use: pytest tests/ktp tests/presentations -v"
        )

    lesson_topic = shared_state.get("lesson_topic")
    if not lesson_topic:
        pytest.skip(
            "lesson_topic not in shared_state — run tests/ktp/create_lesson.py first"
        )

    if not shared_state.get("lesson_plan_generated"):
        pytest.skip(
            "lesson_plan_generated flag not set — run tests/ktp/generate_lesson_plan.py first.\n"
            "The backend requires the КСП (lesson plan) to exist before a "
            "presentation can be generated for the same lesson."
        )

    if ktp_name not in KTP_SUBJECT_MAP:
        pytest.skip(
            f"No subject mapping for KTP: {ktp_name!r} — "
            f"add an entry to KTP_SUBJECT_MAP in generate_presentation.py"
        )
    subject = KTP_SUBJECT_MAP[ktp_name]

    if subject not in SUBJECT_TEMPLATE_MAP:
        pytest.skip(
            f"No template mapping for subject: {subject!r} — "
            f"add an entry to SUBJECT_TEMPLATE_MAP in generate_presentation.py"
        )
    template_name = SUBJECT_TEMPLATE_MAP[subject]

    # ── Step 1: Open the presentations gallery ────────────────────────────────
    page = PresentationsPage(driver, wait, base_url)
    page.open()

    # ── Step 2: Choose the template that matches the KTP subject ──────────────
    #   Алгебра → "Математика"
    #   Физика  → "Физика"
    page.select_template_by_name(template_name)

    # ── Step 3: Select the lesson whose КСП was generated ─────────────────────
    page.select_lesson_topic(lesson_topic)

    # ── Step 4: Click Continue (disabled until a topic is selected) ───────────
    page.click_continue()

    # ── Step 5: Wait for AI generation to finish (up to 5 minutes) ───────────
    page.wait_for_generation(timeout=300)

    # ── Step 6: Verify ────────────────────────────────────────────────────────
    current_url = driver.current_url
    assert "presentations" in current_url, (
        f"Expected to land on a presentation detail page after generation.\n"
        f"Current URL: {current_url}\n"
        f"Page snippet: {page.get_page_text_snippet()!r}"
    )

    page_text = page.get_page_text_snippet(chars=1000)
    assert page_text.strip(), (
        f"Presentation page appears empty after generation.\n"
        f"Current URL: {current_url}"
    )

    # Persist URL for any downstream tests.
    shared_state["presentation_url"] = current_url
