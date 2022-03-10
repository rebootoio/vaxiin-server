from flask import current_app as app

from models.action import Action
from exceptions.base import ActionNotFound, ActionAlreadyExist


def get_by_name(name):
    action = app.session.query(Action).filter(Action.name == name).first()
    if action is None:
        app.logger.debug(f"Action not found! name: '{name}'")
        raise ActionNotFound(name)
    else:
        return action


def create(**kwargs):
    name = kwargs['name']
    try:
        action = get_by_name(name)
    except ActionNotFound:
        app.logger.debug(f"Creating Action {name}...")
    else:
        raise ActionAlreadyExist(name)

    action = Action(**kwargs)
    app.logger.debug(f"Updating Action in DB - {action}")
    app.session.add(action)
    app.session.commit()

    return action


def update(**kwargs):
    name = kwargs['name']
    action = get_by_name(name)
    for key, val in kwargs.items():
        setattr(action, key, val)

    app.logger.debug(f"Updating Action in DB - {action}")
    app.session.commit()

    return action


def get_all():
    action_list = app.session.query(Action).all()
    return action_list


def delete_by_name(name):
    action = get_by_name(name)
    app.logger.debug(f"Deleting action from DB - {action}")
    app.session.delete(action)
    app.session.commit()
    return action
