from flask import current_app as app

from models.device import Device
import services.creds as creds_service
from exceptions.base import DeviceNotFound, DeviceAlreadyExist, CredsNameNotFound


def get_all():
    device_list = app.session.query(Device).all()
    return device_list


def get_zombies():
    device_list = app.session.query(Device).filter(Device.zombie.is_(True)).all()
    return device_list


def get_by_uid(uid):
    device = app.session.query(Device).get(uid)
    if device is None:
        app.logger.debug(f"Device not found! uid: '{uid}'")
        raise DeviceNotFound(uid)
    else:
        return device


def delete_by_uid(uid):
    device = get_by_uid(uid)
    app.session.delete(device)
    app.session.commit()
    app.logger.debug(f"Deleting device from DB - {device}")
    return device


def create(**kwargs):
    uid = kwargs['uid']
    try:
        device = get_by_uid(uid)
    except DeviceNotFound:
        app.logger.debug(f"Creating device - {uid}")
    else:
        raise DeviceAlreadyExist(uid)

    device = Device(**kwargs)
    if device.creds_name is None:
        device.creds_name = creds_service.DEFAULT_CRED_NAME
    else:
        creds_service.get_by_name(kwargs['creds_name'])

    app.logger.info(f"Updating Device in DB - {device}")
    app.session.add(device)
    app.session.commit()
    return device


def update(**kwargs):
    device = get_by_uid(kwargs['uid'])
    if kwargs.get('creds_name') is not None and kwargs.get('creds_name') != creds_service.DEFAULT_CRED_NAME:
        creds_service.get_by_name(kwargs['creds_name'])

    for key, val in kwargs.items():
        setattr(device, key, val)

    app.logger.info(f"Updating Device in DB - {device}")
    app.session.commit()
    return device


def heartbeat(**kwargs):
    invalid_creds = False
    kwargs['zombie'] = False
    creds_name = kwargs.get('creds_name')
    if creds_name is None:
        kwargs.pop('creds_name')
    else:
        if creds_name != creds_service.DEFAULT_CRED_NAME:
            try:
                creds_service.get_by_name(creds_name)
            except CredsNameNotFound:
                app.logger.warn(f"Got heartbeat from uid '{kwargs['uid']}' with invalid cred name '{creds_name}', omitting it")
                kwargs.pop('creds_name')
                invalid_creds = True

    try:
        get_by_uid(kwargs['uid'])
    except DeviceNotFound:
        create(**kwargs)
    else:
        update(**kwargs)

    return invalid_creds


def get_devices_with_creds(creds_name):
    devices = app.session.query(Device).filter(Device.creds_name == creds_name).all()
    return devices


def get_devices_with_heartbeat_timestamp():
    devices = app.session.query(Device).filter(Device.heartbeat_timestamp.isnot(None)).all()
    return devices
