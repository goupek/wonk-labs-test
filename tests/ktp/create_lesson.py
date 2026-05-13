import re
import time as _time

from selenium.webdriver.common.by import By

from pages.ktp.ktp_page import KtpPage
from pages.ktp.add_lesson_modal import AddLessonModal

# ---------------------------------------------------------------------------
# Lesson topic keyed by KTP name — must match KTP_LIST names in test_create_ktp
# ---------------------------------------------------------------------------
LESSON_TOPIC_BY_KTP = {
    # ── Математика ───────────────────────────────────────────────────────────
    "Тригонометрия":             "Синус, косинус және тангенс",
    "Квадрат теңдеулер":         "Дискриминант арқылы квадрат теңдеуді шешу",
    "Функциялар мен графиктер":  "Функцияның графигін салу",
    "Туынды":                    "Туынды және оның геометриялық мағынасы",
    "Геометриялық салулар":      "Циркуль мен сызғыш арқылы геометриялық салулар",
    "Логарифмдер":               "Логарифм және оның қасиеттері",
    # ── Физика ───────────────────────────────────────────────────────────────
    "Гравитация":                "Бүкіләлемдік тартылыс заңы",
    "Ньютон заңдары":            "Ньютонның бірінші заңы",
    "Механикалық қозғалыс":      "Бірқалыпты түзусызықты қозғалыс",
    "Қысым және күш":            "Қысым және күш ұғымдары",
    "Электр тогы":               "Электр тізбегі және оның элементтері",
    "Оптика":                    "Жарық және оның таралуы",
    "Жылулық құбылыстар":        "Жылу алмасу және оның түрлері",
}
# ---------------------------------------------------------------------------

START_TIME = "12:00"
END_TIME   = "13:30"


def test_add_lesson(driver, wait, base_url, login, shared_state):
    ktp_url = shared_state.get("ktp_url")
    assert ktp_url, "ktp_url not set — run test_create_ktp first"

    ktp_name = shared_state.get("ktp_name")
    assert ktp_name, "ktp_name not set — run test_create_ktp first"
    assert ktp_name in LESSON_TOPIC_BY_KTP, f"No lesson topic for KTP: {ktp_name!r}"

    lesson_topic = LESSON_TOPIC_BY_KTP[ktp_name]

    driver.get(ktp_url)
    wait.until(lambda d: "/ru/ktp/" in d.current_url)

    ktp = KtpPage(driver, wait, base_url)
    ktp.click_add_lesson()

    modal = AddLessonModal(driver, wait, base_url)
    modal.wait_open()
    modal.fill_topic(lesson_topic)
    modal.select_today()
    modal.set_time(START_TIME, END_TIME)
    modal.submit()

    # After creation the app may stay on the KTP page — click the lesson by topic.
    _time.sleep(1)  # brief pause for modal animation + list refresh

    if not re.search(r'/ktp/\d+/\d+', driver.current_url):
        # App stayed on KTP list — click the lesson row by its topic text
        lesson_link = wait.until(
            lambda d: d.find_elements(By.XPATH,
                f"//*[contains(text(), '{lesson_topic}')]")
        )
        lesson_link[0].click()
        wait.until(lambda d: re.search(r'/ktp/\d+/\d+', d.current_url))

    shared_state["lesson_url"]   = driver.current_url
    shared_state["lesson_topic"] = lesson_topic
