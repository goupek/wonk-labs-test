import random

from selenium.common.exceptions import TimeoutException

from pages.ktp.ktp_page import KtpPage
from pages.ktp.create_ktp_modal import CreateKtpModal

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------
KTP_LIST = [
   
    # ── Математика ──────────────────────────────────────────────────────────
    ("Тригонометрия",                "Алгебра", "8 класс",  "4 четверть"),
    ("Квадрат теңдеулер",            "Алгебра", "7 класс",  "4 четверть"),
    ("Функциялар мен графиктер",     "Алгебра", "6 класс",  "4 четверть"),
    ("Туынды",                       "Алгебра", "10 класс", "4 четверть"),
    ("Геометриялық салулар",         "Алгебра", "11 класс", "4 четверть"),
    ("Логарифмдер",                  "Алгебра", "9 класс",  "4 четверть"),

    # ── Физика ──────────────────────────────────────────────────────────────
    ("Гравитация",                   "Физика",  "9 класс",  "4 четверть"),
    ("Ньютон заңдары",               "Физика",  "7 класс",  "4 четверть"),
    ("Механикалық қозғалыс",         "Физика",  "8 класс",  "4 четверть"),
    ("Қысым және күш",               "Физика",  "4 класс",  "4 четверть"),
    ("Электр тогы",                  "Физика",  "5 класс",  "4 четверть"),
    ("Оптика",                       "Физика",  "1 класс",  "4 четверть"),
    ("Жылулық құбылыстар",           "Физика",  "10 класс", "4 четверть"),
]
# ---------------------------------------------------------------------------

def test_create_ktp(driver, wait, base_url, login, shared_state):
    """Create a KTP and capture its detail URL.

    The dev backend occasionally fails to register a newly-created KTP
    (commonly seen with low-grade Physics combinations that lack AI
    templates).  When that happens the KTP card never appears in the list
    and ``open_by_name`` times out — in which case we retry with a
    different randomly-chosen KTP up to 3 times before failing.
    """
    last_error = None
    tried = set()

    for attempt in range(3):
        # Pick a KTP we haven't tried yet
        candidates = [k for k in KTP_LIST if k[0] not in tried]
        if not candidates:
            break
        name, subject, grade, quarter = random.choice(candidates)
        tried.add(name)

        try:
            ktp = KtpPage(driver, wait, base_url)
            ktp.open_from_dashboard()
            ktp.click_add_ktp()

            modal = CreateKtpModal(driver, wait, base_url)
            modal.wait_open()
            modal.fill_name(name)
            modal.select_subject(subject)
            modal.select_grade(grade)
            modal.select_quarter(quarter)
            modal.submit()

            # The list shows cards labelled by Subject/Grade/Quarter — not
            # by the typed topic name.  Pass all three so the search can
            # match the actual card text.
            ktp.open_by_name(name, subject=subject, grade=grade, quarter=quarter)
            shared_state["ktp_url"] = driver.current_url
            shared_state["ktp_name"] = name
            return  # success
        except (TimeoutError, TimeoutException) as e:
            last_error = e
            # Try a different KTP on the next attempt.
            # Failure modes covered:
            #  - TimeoutError: card never appeared in the list
            #  - TimeoutException: card was clicked but URL never changed
            #    (clicked the wrong wrapper element)
            continue

    raise AssertionError(
        f"Could not create a KTP after {len(tried)} attempts "
        f"(tried: {sorted(tried)}). Last error: {last_error}"
    )
