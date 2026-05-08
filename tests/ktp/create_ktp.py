import random

from pages.ktp.ktp_page import KtpPage
from pages.ktp.create_ktp_modal import CreateKtpModal

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------
KTP_LIST = [
    # ── Математика ──────────────────────────────────────────────────────────
    ("Тригонометрия",             "Алгебра",          "8 класс", "4 четверть"),
    ("Квадратные уравнения",      "Алгебра",          "7 класс", "4 четверть"),
    ("Функции и графики",          "Алгебра",          "6 класс", "4 четверть"),
    ("Производная",               "Алгебра",          "10 класс", "4 четверть"),
    ("Геометрические построения", "Алгебра",          "11 класс", "4 четверть"),
    ("Логарифмы",                 "Алгебра",          "9 класс", "4 четверть"),

    # ── Физика ──────────────────────────────────────────────────────────────
    ("Гравитация",                    "Физика",              "9 класс", "4 четверть"),
    ("Законы Ньютона",                "Физика",              "7 класс", "4 четверть"),
    ("Механическое движение",         "Физика",              "8 класс", "4 четверть"),
    ("Давление и сила",               "Физика",              "4 класс", "4 четверть"),
    ("Электрический ток",             "Физика",              "5 класс", "4 четверть"),
    ("Оптика",                        "Физика",              "1 класс", "4 четверть"),
    ("Тепловые явления",              "Физика",              "10 класс", "4 четверть"),
]
# ---------------------------------------------------------------------------


def test_create_ktp(driver, wait, base_url, login, shared_state):
    name, subject, grade, quarter = random.choice(KTP_LIST)

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

    # The app stays on the KTP list after creation.
    # Find the new KTP by name, click it, then capture the detail-page URL.
    ktp.open_by_name(name)
    shared_state["ktp_url"]  = driver.current_url
    shared_state["ktp_name"] = name
