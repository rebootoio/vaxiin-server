import re
import services.action as action_service
import services.rule as rule_service
import services.device as device_service
import services.state as state_service
import services.work as work_service
import services.creds as creds_service

from exceptions.base import ActionInUse, CredsInUse, DeviceInUse, StateNotFoundForDevice, RegexIsInvalid, CredsNameIsReserved, UnknownActionParamKey, UnknownActionParamValue, UnknownActionCredStoreValue

VALID_PARAMS = {
    'device': ["uid", "ipmi_ip", "model"],
    'cred': ["username", "password"],
    'cred_store': ["username", "password"],
    'metadata': []
}


def validate_rule_actions(*, action_name_list):
    for action_name in action_name_list:
        action_service.get_by_name(action_name)


def validate_rule_state_id(*, state_id):
    state_service.get_by_id(state_id)


def validate_execution(*, work_id, state_id):
    work_service.get_by_id(work_id)
    if state_id:
        state_service.get_by_id(state_id)


def validate_action_not_in_use(*, action_name):
    rules = rule_service.get_rules_with_action(action_name)
    if rules:
        raise ActionInUse(action_name, {rule.name for rule in rules})


def validate_creds_not_in_use(*, creds_name):
    devices = device_service.get_devices_with_creds(creds_name)
    if devices:
        raise CredsInUse(creds_name, {device.uid for device in devices})


def validate_device_not_in_use(*, device_uid):
    try:
        state = state_service.get_open_by_device(device_uid)
    except StateNotFoundForDevice:
        pass
    else:
        raise DeviceInUse(device_uid, state.state_id)


def validate_regex(*, regex_string):
    try:
        re.compile(regex_string)
    except re.error as err:
        raise RegexIsInvalid(regex_string, f"{err.msg} at position {err.pos}")


def validate_creds_name(*, creds_name):
    if creds_name == creds_service.DEFAULT_CRED_NAME:
        raise CredsNameIsReserved(creds_name)


def validate_action_data_params(*, action_data):
    match_list = re.findall(r'\{([^:}]*?)::([^}]*?)(::([^}]*?))?\}', str(action_data))
    for match in match_list:
        if match[0] in VALID_PARAMS:
            if match[0] == "cred_store":
                if match[3] not in VALID_PARAMS[match[0]]:
                    raise UnknownActionCredStoreValue(match[0], match[1], match[3])
            elif VALID_PARAMS[match[0]] and match[1] not in VALID_PARAMS[match[0]]:
                raise UnknownActionParamValue(match[0], match[1])
        else:
            raise UnknownActionParamKey(match[0])
