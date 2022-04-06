import re
import time
import base64
import requests
import subprocess
from flask import current_app as app
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from subprocess import PIPE, CalledProcessError, TimeoutExpired

import services.state as state_service
from exceptions.handler import ActionError, GetScreenshotError, SendScreenshotError, IpmitoolError, SleepError, KeystrokeError, HttpRequestError


model_to_interface_mapping = {
    'idrac9': 'lanplus',
    'ilo5': 'lanplus',
    'ilo4': 'lanplus',
    'x10': 'lan'
}


def run_action(*, action_type, action_data, device_data, browser):
    action_type_to_func_mapping = {
        'keystroke': run_keystroke_action,
        'ipmitool': run_ipmitool_action,
        'power': run_power_action,
        'screenshot': run_screenshot_action,
        'sleep': run_sleep_action,
        'request': run_request_action
    }
    try:
        action_run_data = action_type_to_func_mapping[action_type](
            action=action_data,
            device=device_data,
            browser=browser
        )
    except ActionError as err:
        app.logger.error(f"Failed at run action - action_type: '{action_type}', action_data: '{action_data}', error: '{err.error}'")
        return 'failure', err.error
    except Exception as err:
        app.logger.error(f"Failed at run action - action_type: '{action_type}', action_data: '{action_data}', error: '{err}'")
        return 'failure', {'error': f"{err}"}
    else:
        return 'success', action_run_data


def run_request_action(*, action, device, browser):
    try:
        res = requests.get(action)
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        app.logger.error(f"Recieved HTTP error: {err}")
        raise HttpRequestError({"error": "HTTP Error", "status_code": res.status_code, "response": res.text})
    except requests.exceptions.ConnectionError as err:
        app.logger.error(f"Recieved Connection error: {err}")
        raise HttpRequestError({"error": "Connection Error", "message": f"{err}"})
    except requests.exceptions.Timeout as err:
        app.logger.error(f"Recieved Timeout error: {err}")
        raise HttpRequestError({"error": "Timeout Error", "message": f"{err}"})
    except requests.exceptions.RequestException as err:
        app.logger.error(f"Recieved Request error: {err}")
        raise HttpRequestError({"error": "Request Error", "message": f"{err}"})

    return {
        'status_code': res.status_code,
        'response': res.text
    }


def run_sleep_action(*, action, device, browser):
    try:
        app.logger.debug(f"Sleeping for {action} seconds")
        time.sleep(int(action))
    except ValueError:
        raise SleepError({
            "message": "Error while trying to sleep",
            "error": f"Failed to pasrse {action} to an integer"
        })
    return {}


def run_keystroke_action(*, action, device, browser):
    app.logger.debug(f"Running keystroke action of '{action}' on uid {device['uid']}")
    key_combo_list = action.split(';')

    for key_combo in key_combo_list:
        action_chain = ActionChains(browser)

        # Check if key combo includes special key followed by '+' (if so we will need to perform key_down logic)
        special_keys_match = re.match(r'^keys.([a-z0-9_]+)(\+)?', key_combo, flags=re.IGNORECASE)

        # No special keys
        if special_keys_match is None:
            for char in key_combo:
                _add_char_to_action_chain(action_chain, char)

        # special key without '+' - just press it
        elif special_keys_match[2] is None:
            try:
                parsed_special_key = getattr(Keys, special_keys_match[1].upper())
            except AttributeError as err:
                raise KeystrokeError({
                    "message": "Error while trying parse keystroke special key",
                    "error": str(err)
                })
            action_chain.send_keys(parsed_special_key).pause(app.config.get('pause_between_keys'))

        # special key with '+' - Hold down all keys, press last and release keys
        else:
            key_list = key_combo.split('+')
            try:
                parsed_key_list = [
                    re.sub(r'keys.([a-z0-9_]+)(\+|$)', lambda m: getattr(Keys, m.group(1).upper()), key, flags=re.IGNORECASE)
                    for key in key_list]
            except AttributeError as err:
                raise KeystrokeError({
                    "message": "Error while trying parse keystroke special key",
                    "error": str(err)
                })

            for idx in range(len(parsed_key_list) - 1):
                action_chain.key_down(parsed_key_list[idx])

            _add_char_to_action_chain(action_chain, parsed_key_list[-1])

            for idx in range(len(parsed_key_list) - 1):
                action_chain.key_up(parsed_key_list[idx])

            action_chain.pause(app.config.get('pause_between_keys'))

        action_chain.perform()

    return {}


def run_ipmitool_action(*, action, device, browser):
    app.logger.debug(f"Running ipmitool action of '{action}' on uid {device['uid']}")
    command = ['ipmitool', '-H', device['ip'], '-U', device['username'], '-P', device['password'], '-I', model_to_interface_mapping.get(device['model'].lower(), 'lan')]
    command += action.split(' ')

    try:
        result = subprocess.run(
            command,
            stdout=PIPE,
            stderr=PIPE,
            check=False,
            encoding="utf-8",
            timeout=30
        )

        result.check_returncode()
    except OSError as err:
        app.logger.error(f"Recieved OS error on ipmitool command: {err}")
        raise IpmitoolError({
            "message": "OS error",
            "error": err.strerror
        })

    except TimeoutExpired as err:
        app.logger.error(f"Recieved timeout on ipmitool command: {err}")
        raise IpmitoolError({
            "message": "Timeout error",
            "error": err.strerror
        })

    except CalledProcessError as err:
        app.logger.error(f"Recieved non-zero return code on ipmitool command: {err}")
        raise IpmitoolError({
            "message": "Exit status error",
            "stdout": result.stdout,
            "stderr": result.stderr
        })

    app.logger.debug(f"ipmitool command completed. stdout: '{result.stdout}'. stderr: '{result.stderr}'")
    return {
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def run_power_action(*, action, device, browser):
    app.logger.debug(f"Running power action of '{action}' on uid {device['uid']}")
    return run_ipmitool_action(action=f"power {action}", device=device, browser=browser)


def run_screenshot_action(*, action, device, browser):
    app.logger.debug(f"Running screenshot action for uid '{device['uid']}'")
    time.sleep(15)
    try:
        screenshot = browser.get_screenshot_as_png()
    except Exception as err:
        app.logger.error(f"Error while taking screenshot: {err}")
        raise GetScreenshotError({
            'message': 'Failed to get screenshot',
            'error': err.strerror
        })

    try:
        state_service.create_or_update(
            device_uid=device['uid'],
            screenshot=base64.b64encode(screenshot).decode('ascii'),
            resolved=None
        )
    except Exception as err:
        app.logger.error(f"Error while sending screenshot to server: {err}")
        raise SendScreenshotError(err)

    return {}


def _add_char_to_action_chain(action_chain, char):
    regex_for_shift = re.compile(r'[~!@#$%^&*()_+|}{":?><A-Z]')
    if regex_for_shift.search(char) is None:
        action_chain.send_keys(char).pause(1)
    else:
        action_chain.key_down(Keys.SHIFT).send_keys(char).key_up(Keys.SHIFT).pause(1)
