import werkzeug
from flask_restplus import reqparse, inputs


def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s


def get_base_parser():
    parser = reqparse.RequestParser()
    return parser.copy()


def get_name_parser():
    parser = get_base_parser()
    parser.add_argument('name', required=True, location='args', type=non_empty_string)

    return parser.copy()


def get_id_parser():
    parser = get_base_parser()
    parser.add_argument('id', required=True, location='args', type=int)

    return parser.copy()


def get_uid_parser():
    parser = get_base_parser()
    parser.add_argument('uid', required=True, location='args', type=non_empty_string)

    return parser.copy()


def get_regex_parser():
    parser = get_base_parser()
    parser.add_argument('regex', required=True, location='args', type=non_empty_string)

    return parser.copy()


def get_work_complete_parser():
    parser = get_base_parser()
    parser.add_argument('work_id', required=True, location='json', type=int)
    parser.add_argument('status', required=True, location='json', type=non_empty_string, choices=('success', 'failure'))

    return parser.copy()


def get_action_request_parser():
    parser = get_base_parser()
    parser.add_argument('name', required=True, location='json', type=str)
    parser.add_argument('action_type', required=True, location='json', type=non_empty_string, choices=('keystroke', 'ipmitool', 'power', 'sleep'))
    parser.add_argument('action_data', required=True, location='json')

    return parser.copy()


def get_rule_request_parser():
    parser = get_base_parser()
    parser.add_argument('name', required=True, location='json', type=non_empty_string)
    parser.add_argument('state_id', required=True, location='json', type=int)
    parser.add_argument('regex', required=True, location='json', type=non_empty_string)
    parser.add_argument('actions', required=True, location='json', type=list)
    parser.add_argument('ignore_case', required=False, location='json', type=bool, default=True)
    parser.add_argument('enabled', required=False, location='json', type=bool, default=True)
    parser.add_argument('after_rule', required=False, location='json', type=non_empty_string)
    parser.add_argument('before_rule', required=False, location='json', type=non_empty_string)

    return parser.copy()


def get_rule_update_request_parser():
    parser = get_base_parser()
    parser.add_argument('name', required=True, location='json', type=non_empty_string)
    parser.add_argument('state_id', required=False, location='json', type=int)
    parser.add_argument('regex', required=False, location='json', type=non_empty_string)
    parser.add_argument('actions', required=False, location='json', type=list)
    parser.add_argument('ignore_case', required=False, location='json', type=bool)
    parser.add_argument('enabled', required=False, location='json', type=bool)
    parser.add_argument('after_rule', required=False, location='json', type=non_empty_string)
    parser.add_argument('before_rule', required=False, location='json', type=non_empty_string)

    return parser.copy()


def get_state_request_parser():
    parser = get_base_parser()
    parser.add_argument('device_uid', required=True, location='json', type=non_empty_string)
    parser.add_argument('screenshot', required=True, location='json', type=non_empty_string)

    return parser.copy()


def get_state_file_request_parser():
    parser = get_base_parser()
    parser.add_argument('device_uid', required=True, location='args', type=non_empty_string)
    parser.add_argument('screenshot', required=True, location='files', type=werkzeug.datastructures.FileStorage)

    return parser.copy()


def get_state_resolved_parser():
    parser = get_base_parser()
    parser.add_argument('state_id', required=True, location='json', type=int)
    parser.add_argument('resolved', required=True, location='json', type=bool)

    return parser.copy()


def get_execution_request_parser():
    parser = get_base_parser()
    parser.add_argument('work_id', required=True, location='json', type=int)
    parser.add_argument('state_id', required=True, location='json', type=int)
    parser.add_argument('action_name', required=True, location='json', type=non_empty_string)
    parser.add_argument('trigger', required=True, location='json', type=non_empty_string)
    parser.add_argument('status', required=True, location='json', type=non_empty_string, choices=('success', 'failure'))
    parser.add_argument('run_data', required=True, location='json', type=dict)
    parser.add_argument('elapsed_time', required=True, location='json', type=float)

    return parser.copy()


def get_device_parser():
    parser = get_base_parser()
    parser.add_argument('uid', required=True, location='json', type=non_empty_string)
    parser.add_argument('ipmi_ip', required=True, location='json', type=non_empty_string)
    parser.add_argument('model', required=True, location='json', type=non_empty_string)
    parser.add_argument('creds_name', required=False, location='json', type=str)
    parser.add_argument('zombie', required=False, location='json', type=bool)

    return parser.copy()


def get_creds_parser():
    parser = get_base_parser()
    parser.add_argument('name', required=True, location='json', type=non_empty_string)
    parser.add_argument('username', required=True, location='json', type=non_empty_string)
    parser.add_argument('password', required=True, location='json', type=non_empty_string)

    return parser.copy()


def get_work_request_parser():
    parser = get_base_parser()
    parser.add_argument('device_uid', required=True, location='json', type=non_empty_string)
    parser.add_argument('actions', required=False, location='json', type=list)
    parser.add_argument('rule', required=False, location='json', type=non_empty_string)

    return parser.copy()


def get_state_filter_parser():
    parser = get_base_parser()
    parser.add_argument('uid', required=False, location='args', type=non_empty_string)
    parser.add_argument('type', required=False, location='args', type=non_empty_string)
    parser.add_argument('regex', required=False, location='args', type=non_empty_string)

    return parser.copy()


def get_agent_heartbeat_request_parser():
    parser = get_base_parser()
    parser.add_argument('uid', required=True, location='json', type=non_empty_string)
    parser.add_argument('agent_version', required=True, location='json', type=non_empty_string)
    parser.add_argument('heartbeat_timestamp', required=True, location='json', type=inputs.datetime_from_iso8601)
    parser.add_argument('ipmi_ip', required=True, location='json', type=non_empty_string)
    parser.add_argument('model', required=True, location='json', type=non_empty_string)
    parser.add_argument('creds_name', required=False, location='json', type=non_empty_string)

    return parser.copy()
