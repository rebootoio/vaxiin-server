import re
import io
import base64
import pytesseract
from PIL import Image
from flask import current_app as app

from models.state import State
from exceptions.base import StateNotFound, StateNotFoundForDevice


def get_by_id(state_id):
    state = app.session.query(State).get(state_id)
    if state is None:
        app.logger.debug(f"State not found by id: '{state_id}'")
        raise StateNotFound(state_id)
    else:
        return state


def get_by_device(device_uid):
    state = app.session.query(State).filter(State.device_uid == device_uid).order_by(State.state_id.desc()).first()
    if state is None:
        app.logger.debug(f"State not found by device uid: '{device_uid}'")
        raise StateNotFoundForDevice(device_uid)
    else:
        return state


def get_open_by_device(device_uid):
    state = app.session.query(State).filter(State.device_uid == device_uid, State.resolved.is_(False)).first()
    if state is None:
        app.logger.debug(f"State not found by device uid: '{device_uid}'")
        raise StateNotFoundForDevice(device_uid)
    else:
        return state


def resolve_by_device(device_uid):
    state = app.session.query(State).filter(State.device_uid == device_uid, State.resolved.is_(False)).first()
    if state is None:
        app.logger.debug(f"State not found by device uid: '{device_uid}'")
        raise StateNotFoundForDevice(device_uid)
    else:
        state.resolved = True

    app.session.commit()
    return state


def update_resolved_by_id(*, state_id, resolved):
    state = get_by_id(state_id)
    state.resolved = resolved

    app.session.commit()
    return state


def get_all(device_uid=None, regex=None):
    if device_uid is None:
        state_list = app.session.query(State).all()
    else:
        state_list = app.session.query(State).filter(State.device_uid == device_uid).all()

    return _filter_by_regex(state_list, regex)


def get_open(device_uid=None, regex=None):
    if device_uid is None:
        state_list = app.session.query(State).filter(State.resolved.is_(False)).all()
    else:
        state_list = app.session.query(State).filter(State.resolved.is_(False), State.device_uid == device_uid).all()

    return _filter_by_regex(state_list, regex)


def get_resolved(device_uid=None, regex=None):
    if device_uid is None:
        state_list = app.session.query(State).filter(State.resolved.is_(True)).all()
    else:
        state_list = app.session.query(State).filter(State.resolved.is_(True), State.device_uid == device_uid).all()

    return _filter_by_regex(state_list, regex)


def get_unknown(device_uid=None, regex=None):
    if device_uid is None:
        state_list = app.session.query(State).filter(State.resolved.is_(False), State.matched_rule.is_(None)).all()
    else:
        state_list = app.session.query(State).filter(State.resolved.is_(False), State.matched_rule.is_(None), State.device_uid == device_uid).all()

    return _filter_by_regex(state_list, regex)


def _filter_by_regex(state_list, regex):
    if regex is None:
        return state_list

    matched_state_list = []
    compiled_regex = re.compile(regex, re.IGNORECASE)

    for state in state_list:
        match = compiled_regex.search(state.ocr_text)
        if match:
            matched_state_list.append(state)

    return matched_state_list


def create_or_update(*, device_uid, screenshot):
    # TODO - handle and throw DeviceNotFound Error
    decoded_screenshot = base64.b64decode(screenshot.encode('ascii'))
    ocr_text = pytesseract.image_to_string(Image.open(io.BytesIO(decoded_screenshot)))

    try:
        state = get_open_by_device(device_uid)

    except StateNotFoundForDevice:
        state = State(
            screenshot=decoded_screenshot,
            ocr_text=ocr_text,
            device_uid=device_uid
        )
        app.session.add(state)

    else:
        state.screenshot = decoded_screenshot
        state.ocr_text = ocr_text

    app.session.commit()
    return state
