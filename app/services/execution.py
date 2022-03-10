from flask import current_app as app

from models.execution import Execution


def create(**kwargs):
    execution = Execution(**kwargs)
    app.logger.debug(f"Updating Execution in DB - {execution}")
    app.session.add(execution)
    app.session.commit()

    return execution


def get_by_work_id(work_id):
    execution_list = app.session.query(Execution).filter(Execution.work_id == work_id).all()
    return execution_list
