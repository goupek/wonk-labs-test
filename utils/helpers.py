import platform
import time

from selenium.webdriver.common.keys import Keys

SELECT_ALL = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL


def js_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", el)
