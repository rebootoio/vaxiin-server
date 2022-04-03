import datetime
from flask import current_app as app

import services.work as work_service
import services.rule as rule_service
import services.state as state_service
import services.device as device_service
import services.action as action_service
import services.execution as execution_service

from exceptions.base import WorkNotFoundForDevice, WorkAlreadyExistForDevice, ManualWorkMustHaveRuleOrActions


def create_manual_work_for_device(*, device_uid, rule, actions):
    try:
        work_service.get_by_device(device_uid)
    except WorkNotFoundForDevice:
        app.logger.debug(f"creaing work for device uid - {device_uid}")
    else:
        raise WorkAlreadyExistForDevice(device_uid)

    device_service.get_by_uid(device_uid)

    if rule is not None:
        rule = rule_service.get_by_name(rule)
        work_data = parse_work(
            state=None,
            device_uid=device_uid,
            rule=rule,
            trigger=f"Manual - Rule: {rule.name}"
        )
    elif actions is not None:
        work_data = parse_work(
            state=None,
            device_uid=device_uid,
            actions=actions,
            trigger=f"Manual - Actions: {', '.join(actions)}"
        )
    else:
        raise ManualWorkMustHaveRuleOrActions()

    return work_data


def parse_work(*, state, device_uid, rule=None, actions=None, trigger):
    action_list = []
    action_type_set = set()

    if rule is not None:
        actions_data = rule.actions
    else:
        actions_data = actions

    for action_name in actions_data:
        action = action_service.get_by_name(action_name)
        action_list.append({
            'name': action.name,
            'type': action.action_type,
            'data': action.action_data
        })
        action_type_set.add(action.action_type)

    work_data = {
        'state_id': state.state_id if state else None,
        'device_uid': device_uid,
        'actions': action_list,
        'trigger': trigger,
        'requires_console': 'keystroke' in action_type_set or 'screenshot' in action_type_set
    }

    return work_data


def fail_stuck_work(a_app):
    with a_app.app_context():
        current_time = datetime.datetime.now()
        work_list = work_service.get_assingned_and_pending()
        for work in work_list:
            if (current_time - work.assigned).total_seconds() / 60 > app.config.get('pending_work_timeout'):
                execution_service.create(
                    work_id=work.work_id,
                    state_id=work.state_id,
                    action_name="Timeout Exceeded",
                    trigger=work.trigger,
                    elapsed_time=(current_time - work.assigned).total_seconds(),
                    status="failure",
                    run_data={
                        'message': "Got a timeout while waiting for assigned work to complete"
                    }
                )
                work_service.complete_by_id(work_id=work.work_id, status="failure")


def periodic_work_assignment(a_app):
    with a_app.app_context():
        current_time = datetime.datetime.now()
        work_data_list = []
        open_state_list = state_service.get_open()

        for state in open_state_list:
            if (state.matched_rule is not None and all(
                    [work.status != 'PENDING' and ((current_time - work.last_updated).total_seconds() / 60 > app.config.get('retry_rule_interval')) for work in state.works])):
                matching_rule = rule_service.get_by_name(state.matched_rule)
                work_data_list.append(
                    parse_work(
                        state=state,
                        device_uid=state.device_uid,
                        rule=matching_rule,
                        trigger=f'Rule - {matching_rule.name}'
                    )
                )

        if work_data_list:
            work_service.create_many(work_data_list)


def get_zombie_screenshots(a_app):
    with a_app.app_context():
        search_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=app.config.get('update_state_interval'))
        work_data_list = []
        device_list = device_service.get_zombies()

        for device in device_list:
            work = work_service.get_by_device_uid_and_trigger_pending_or_after_timestamp(
                device_uid=device.uid,
                trigger='zombie screenshot',
                timestamp=search_timestamp
            )

            if work is None:
                work_data_list.append({
                    'state_id': None,
                    'device_uid': device.uid,
                    'actions': [{
                        'name': 'screenshot',
                        'type': 'screenshot',
                        'data': 'screenshot'
                    }],
                    'trigger': 'zombie screenshot',
                    'requires_console': True
                })

        if work_data_list:
            work_service.create_many(work_data_list)


def mark_zombies(a_app):
    with a_app.app_context():
        device_list = device_service.get_devices_with_heartbeat_timestamp()
        zombie_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=app.config.get('become_zombie_interval'))

        for device in device_list:
            if device.heartbeat_timestamp < zombie_timestamp:
                device_service.update(**{'uid': device.uid, 'zombie': True})
