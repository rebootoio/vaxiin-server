import datetime
from sqlalchemy import or_
from flask import current_app as app

from models.work import Work
import services.creds as creds_service
import services.device as device_service
from exceptions.base import WorkNotFound, WorkNotFoundForDevice, WorkIsNotPending


def get_by_id(work_id):
    work = app.session.query(Work).get(work_id)
    if work is None:
        app.logger.debug(f"Work not found by id: '{work_id}'")
        raise WorkNotFound(work_id)
    else:
        return work


def get_by_device(device_uid):
    work = app.session.query(Work).filter(Work.device_uid == device_uid, Work.status == 'PENDING').first()
    if work is None:
        app.logger.debug(f"Pending Work not found by device uid: '{device_uid}'")
        raise WorkNotFoundForDevice(device_uid)
    else:
        return work


def get_all():
    work_list = app.session.query(Work).all()
    return work_list


def get_pending():
    work_list = app.session.query(Work).filter(Work.status == 'PENDING').all()
    return work_list


def get_completed():
    work_list = app.session.query(Work).filter(Work.status != 'PENDING').all()
    return work_list


def get_all_by_device(device_uid):
    work_list = app.session.query(Work).filter(Work.device_uid == device_uid).all()
    return work_list


def get_by_device_uid_and_trigger_pending_or_after_timestamp(*, device_uid, trigger, timestamp):
    work = app.session.query(Work).filter(
        Work.device_uid == device_uid, Work.trigger == trigger,
        or_(Work.status == 'PENDING', Work.last_updated > timestamp)
    ).first()
    return work


def get_assingned_and_pending():
    work_list = app.session.query(Work).filter(
        Work.status == 'PENDING',
        Work.assigned.isnot(None)
    ).all()
    return work_list


def get_assignment():
    work = app.session.query(Work).filter(Work.status == 'PENDING', Work.assigned.is_(None)).first()
    if work:
        device = device_service.get_by_uid(work.device_uid)
        if device.creds_name == creds_service.DEFAULT_CRED_NAME:
            creds = creds_service.get_default()
        else:
            creds = creds_service.get_by_name(device.creds_name)

        if creds is None:
            app.logger.warning("Not assigning work since no credentials were found")
            return

        assignment = {
            'work_id': work.work_id,
            'state_id': work.state_id,
            'trigger': work.trigger,
            'requires_console': work.requires_console,
            'action_list': work.actions,
            'device_data': {
                'uid': device.uid,
                'ip': device.ipmi_ip,
                'username': creds.username,
                'password': creds.password,
                'model': device.model,
            }
        }

        work.assigned = datetime.datetime.now()
        app.session.commit()

        return assignment


def create(work_data):
    work = Work(**work_data)
    app.logger.debug(f"Creating work '{work}'...")
    app.session.add(work)
    app.session.commit()
    return work


def create_many(work_data_list):
    app.session.bulk_save_objects([Work(**work_data) for work_data in work_data_list])
    app.session.commit()


def complete_by_id(*, work_id, status):
    work = get_by_id(work_id)
    if work.status != "PENDING":
        raise WorkIsNotPending(work_id)

    work.status = status
    app.session.commit()

    return work
