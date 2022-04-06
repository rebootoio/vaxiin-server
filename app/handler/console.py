import os
import time
from flask import current_app as app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from exceptions.handler import ModelNotSupportedError, OpenConsoleError


def open_console(*, uid, ip, username, password, model):
    model_to_func_mapping = {
        'idrac9': open_console_for_idrac9,
        'ilo5': open_console_for_ilo5,
        'ilo4': open_console_for_ilo4,
        'x10': open_console_for_x10
    }

    if model.lower() not in model_to_func_mapping:
        raise ModelNotSupportedError(f"Model '{model}' is not supported")

    app.logger.debug(f"Openning conosle to device with IP '{ip}'")
    browser = webdriver.Firefox(service_log_path=os.devnull)

    try:
        model_to_func_mapping[model.lower()](
            ip=ip,
            username=username,
            password=password,
            browser=browser
        )
    except WebDriverException as err:
        browser.quit()
        app.logger.error(f"WebDriverException caught while trying to open console: {err}")
        raise OpenConsoleError(err.msg)
    except Exception as err:
        browser.quit()
        app.logger.error(f"Exception caught while trying to open console: {err}")
        raise OpenConsoleError(str(err))

    return browser


def close_console(*, browser, model):
    model_to_func_mapping = {
        'ilo5': logout_for_ilo5,
        'ilo4': logout_for_ilo4,
        'x10': logout_for_x10
    }
    if model.lower() in model_to_func_mapping:
        app.logger.debug(f"logging out")
        try:
            model_to_func_mapping[model.lower()](
                browser=browser
            )
        except Exception as err:
            app.logger.error(f"Exception caught while trying to logout: {err}")

    app.logger.debug(f"Closing conosle to device")
    browser.quit()


def open_console_for_idrac9(*, ip, username, password, browser):
    url = f'https://{ip}/restgui/start.html?console'
    browser.get(url)

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.NAME, "username")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see username input element after 30s")

    browser.find_element_by_name('username').send_keys(username)
    browser.find_element_by_name('password').send_keys(password)

    try:
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.cux-button")))
    except TimeoutException:
        raise OpenConsoleError("Failed to get login button clickable after 30s")

    time.sleep(5)
    browser.find_element_by_css_selector('button.cux-button').click()

    try:
        WebDriverWait(browser, 60).until(lambda browser: len(browser.window_handles) == 2)
    except TimeoutException:
        raise OpenConsoleError("Failed to get new console window after 60s")

    browser.switch_to.window(browser.window_handles[1])
    browser.maximize_window()

    try:
        WebDriverWait(browser, 60).until(EC.title_contains("FPS:"))
    except TimeoutException:
        raise OpenConsoleError("Failed to get console viewer opened after 60s")

    time.sleep(5)
    body = browser.find_element_by_tag_name('body')
    body.send_keys(Keys.SHIFT)
    time.sleep(5)


def open_console_for_ilo5(*, ip, username, password, browser):
    url = f'https://{ip}/'
    browser.get(url)

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.NAME, "appFrame")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see login iframe element after 30s")

    browser.switch_to.frame(browser.find_element_by_name('appFrame'))

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "username")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see username input element after 30s")

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "login-form__submit")))
    except TimeoutException:
        raise OpenConsoleError("Failed to get login button clickable after 30s")

    browser.find_element_by_id('username').send_keys(username)
    browser.find_element_by_id('password').send_keys(password)
    browser.find_element_by_id('login-form__submit').click()

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "tabset_rc")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see console navigation element after 30s")

    browser.find_element_by_id('tabset_rc').click()
    browser.switch_to.frame(browser.find_element_by_name('iframeContent'))

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "HRCEXTButton")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see open console in new windown element after 30s")

    browser.find_element_by_id('HRCEXTButton').click()

    try:
        WebDriverWait(browser, 60).until(lambda browser: len(browser.window_handles) == 2)
    except TimeoutException:
        raise OpenConsoleError("Failed to get new console window after 60s")

    browser.switch_to.window(browser.window_handles[1])

    try:
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Acquire')]")))
    except TimeoutException:
        pass
    else:
        raise OpenConsoleError("Console session already opened by someone else")

    browser.maximize_window()
    time.sleep(5)
    body = browser.find_element_by_tag_name('body')
    body.send_keys(Keys.SHIFT)
    time.sleep(5)


def open_console_for_ilo4(*, ip, username, password, browser):
    url = f'https://{ip}/'
    browser.get(url)

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.NAME, "appFrame")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see main app iframe element after 30s")

    browser.switch_to.frame(browser.find_element_by_name('appFrame'))

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "usernameInput")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see username input element after 30s")

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "ID_LOGON")))
    except TimeoutException:
        raise OpenConsoleError("Failed to get login button clickable after 30s")

    browser.find_element_by_id('usernameInput').send_keys(username)
    browser.find_element_by_id('passwordInput').send_keys(password)
    browser.find_element_by_id('ID_LOGON').click()

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "frameContent")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see content frame element after 30s")

    browser.switch_to.frame(browser.find_element_by_id('frameContent'))

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "iframeContent")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see content iframe element after 30s")

    browser.switch_to.frame(browser.find_element_by_id('iframeContent'))

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "html5_irc_label")))
    except TimeoutException:
        raise OpenConsoleError("Failed to get html5 irc element clickable after 30s")

    browser.find_element_by_xpath("//span[@id='html5_irc_label']/a").click()

    browser.switch_to.default_content()
    browser.switch_to.frame(browser.find_element_by_name('appFrame'))

    try:
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Acquire')]")))
    except TimeoutException:
        pass
    else:
        raise OpenConsoleError("Console session already opened by someone else")

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[@langkey='IRC.label.maximize']")))
    except TimeoutException:
        raise OpenConsoleError("Failed to see get the maximize button clicakble after 30s")

    browser.find_element_by_xpath("//div[@langkey='IRC.label.maximize']").click()

    browser.maximize_window()

    time.sleep(5)
    body = browser.find_element_by_id('rc_video')
    body.send_keys(Keys.SHIFT)
    time.sleep(5)


def open_console_for_x10(*, ip, username, password, browser):
    url = f'https://{ip}/'
    browser.get(url)

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.NAME, "name")))
    except TimeoutException:
        OpenConsoleError("Failed to see username input element after 30s")

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.NAME, "pwd")))
    except TimeoutException:
        OpenConsoleError("Failed to see password input element after 30s")

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "login_word")))
    except TimeoutException:
        OpenConsoleError("Failed to get login button clickable after 30s")

    browser.find_element_by_name('pwd').send_keys(password)
    browser.find_element_by_name('name').send_keys(username)
    browser.find_element_by_id('login_word').click()

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "TOPMENU")))
    except TimeoutException:
        OpenConsoleError("Failed to see main frame")

    browser.switch_to.frame(browser.find_element_by_id("TOPMENU"))

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, "remote")))
    except TimeoutException:
        OpenConsoleError("Failed to get Remote Control tab clickable after 30s")

    browser.find_element_by_id("remote").click()

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'iKVM/HTML5')]")))
    except TimeoutException:
        OpenConsoleError("Failed to get Remote Control tab clickable after 30s")

    browser.find_element_by_xpath("//a[contains(text(), 'iKVM/HTML5')]").click()

    try:
        WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "frame_main")))
    except TimeoutException:
        OpenConsoleError("Failed to see iKVM frame after 30s")

    browser.switch_to.frame(browser.find_element_by_id("frame_main"))

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='iKVM/HTML5']")))
    except TimeoutException:
        OpenConsoleError("Failed to get iKVM button clickable after 30s")

    browser.find_element_by_xpath("//input[@value='iKVM/HTML5']").click()

    try:
        WebDriverWait(browser, 60).until(lambda browser: len(browser.window_handles) == 2)
    except TimeoutException:
        OpenConsoleError("Failed to get new console window after 60s")

    browser.switch_to.window(browser.window_handles[1])

    try:
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]")))
    except TimeoutException:
        OpenConsoleError("Failed to get recording warning close button clickable after 30s")

    browser.find_element_by_xpath("//button[contains(text(), 'Close')]").click()

    browser.maximize_window()

    time.sleep(5)
    body = browser.find_element_by_tag_name('body')
    body.send_keys(Keys.SHIFT)
    time.sleep(5)


def logout_for_ilo5(*, browser):
    _close_additional_windows(browser=browser)
    browser.switch_to.window(browser.window_handles[0])
    browser.switch_to.default_content()
    browser.switch_to.frame(browser.find_element_by_name('appFrame'))
    browser.find_element_by_id('userlink').click()
    browser.find_element_by_id('user_logout').click()


def logout_for_ilo4(*, browser):
    browser.find_element_by_xpath("//div[@langkey='IRC.label.restore']").click()
    browser.switch_to.default_content()
    browser.switch_to.frame(browser.find_element_by_name('appFrame'))
    browser.switch_to.frame(browser.find_element_by_name('headerFrame'))
    browser.find_element_by_id('logout_button').click()


def logout_for_x10(*, browser):
    _close_additional_windows(browser=browser)
    browser.switch_to.window(browser.window_handles[0])
    browser.switch_to.default_content()
    browser.switch_to.frame(browser.find_element_by_id("TOPMENU"))
    browser.find_element_by_link_text('Logout').click()


def _close_additional_windows(*, browser):
    open_windows_count = len(browser.window_handles)
    if open_windows_count > 1:
        for i in range(1, open_windows_count):
            browser.switch_to.window(browser.window_handles[i])
            browser.close()
