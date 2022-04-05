import time
from flask import current_app as app

import services.work as work_service
import services.execution as execution_service

import helpers.console as console_helper
import helpers.action_runner as action_runner

from exceptions.handler import ConsoleError


def get_work_assignment(a_app):
    with a_app.app_context():
        assignment = work_service.get_assignment()

        if assignment:
            app.logger.debug(f"Got work assignment: '{assignment}'")
            run_work_assignment(**assignment)
        else:
            app.logger.debug(f"no assignment found")


def run_work_assignment(*, work_id, state_id, trigger, requires_console, device_data, action_list):
    work_status = 'success'
    browser = None

    if requires_console:
        try:
            browser = console_helper.open_console(**device_data)
        except ConsoleError as err:
            execution_service.create(
                work_id=work_id,
                state_id=state_id,
                trigger=trigger,
                action_name='Open Console',
                status='failure',
                run_data={'message': err.message, 'error': err.error},
                elapsed_time=0.0
            )

            work_service.complete_by_id(
                work_id=work_id,
                status='failure'
            )

            return

    for action in action_list:
        app.logger.debug(f"Running action {action['name']}")
        start_time = time.time()
        action_run_status, action_run_data = action_runner.run_action(
            action_type=action['type'],
            action_data=action['data'],
            device_data=device_data,
            browser=browser
        )
        elapsed_time = time.time() - start_time

        execution_service.create(
            work_id=work_id,
            state_id=state_id,
            trigger=trigger,
            action_name=action['name'],
            status=action_run_status,
            run_data=action_run_data,
            elapsed_time=elapsed_time
        )

        if action_run_status != work_status:
            work_status = action_run_status
            break

    if requires_console:
        console_helper.close_console(
            browser=browser,
            model=device_data['model']
        )

    work_service.complete_by_id(
        work_id=work_id,
        status=work_status
    )
