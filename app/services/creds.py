from flask import current_app as app

from models.creds import Creds
from exceptions.base import CredsNameNotFound, CredsAreSetAsDefault, CredsAlreadyExist


DEFAULT_CRED_NAME = "default"


def get_all():
    creds_list = app.session.query(Creds).all()
    return creds_list


def get_by_name(creds_name):
    creds = app.session.query(Creds).filter(Creds.name == creds_name).first()
    if creds is None:
        app.logger.debug(f"Creds not found! name: '{creds_name}'")
        raise CredsNameNotFound(creds_name)
    else:
        return creds


def get_default():
    creds = app.session.query(Creds).filter(Creds.is_default.is_(True)).first()
    return creds


def create(**kwargs):
    name = kwargs['name']
    try:
        creds = get_by_name(name)
    except CredsNameNotFound:
        app.logger.debug(f"Creating creds {name}...")
    else:
        raise CredsAlreadyExist(name)

    creds = Creds(**kwargs)
    if len(get_all()) == 0:
        creds.is_default = True
    app.logger.info(f"Updating Creds in DB - {creds}")
    app.session.add(creds)
    app.session.commit()
    return creds


def update(**kwargs):
    creds = get_by_name(kwargs['name'])
    for key, val in kwargs.items():
        setattr(creds, key, val)

    app.logger.info(f"Updating Creds in DB - {creds}")
    app.session.commit()
    return creds


def delete(creds_name):
    creds = get_by_name(creds_name)
    if creds.is_default:
        raise CredsAreSetAsDefault(creds_name)

    app.session.delete(creds)
    app.session.commit()
    return creds


def set_as_default(creds_name):
    new_default_creds = get_by_name(creds_name)
    current_default_creds = get_default()

    if current_default_creds is not None:
        current_default_creds.is_default = False

    new_default_creds.is_default = True
    app.session.commit()
    return new_default_creds
