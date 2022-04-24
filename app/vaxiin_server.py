import os
import logging
import traceback
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_restplus import Api
from flask import Flask, _app_ctx_stack
from sqlalchemy.orm import scoped_session
from apscheduler.schedulers.background import BackgroundScheduler

from config import configure_app, configure_logging
import helpers.db as db_helper
import helpers.convertor as convertor_helper

import handler.work as work_handler

from routes.creds import ns as creds_ns
from routes.device import ns as device_ns
from routes.action import ns as action_ns
from routes.rule import ns as rule_ns
from routes.state import ns as state_ns
from routes.screenshot import ns as screenshot_ns
from routes.work import ns as work_ns
from routes.execution import ns as execution_ns
from routes.heartbeat import ns as heartbeat_ns
from routes.version import ns as version_ns

from models.creds import Base as creds_base
from models.device import Base as device_base
from models.action import Base as action_base
from models.execution import Base as execution_base
from models.rule import Base as rule_base
from models.state import Base as state_base
from models.work import Base as work_base


default_path = '/api/v1'


def create_app():
    app = Flask(__name__)
    CORS(app)

    api = Api(app, version='1.0', title='Rebooto Recover API',
              description='Rebooto Recover API')

    api.add_namespace(creds_ns, default_path + '/creds')
    api.add_namespace(device_ns, default_path + '/device')
    api.add_namespace(action_ns, default_path + '/action')
    api.add_namespace(rule_ns, default_path + '/rule')
    api.add_namespace(state_ns, default_path + '/state')
    api.add_namespace(screenshot_ns, default_path + '/screenshot')
    api.add_namespace(work_ns, default_path + '/work')
    api.add_namespace(execution_ns, default_path + '/execution')
    api.add_namespace(heartbeat_ns, default_path + '/heartbeat')
    api.add_namespace(version_ns, '/version')

    @app.teardown_appcontext
    def remove_session(*args, **kwargs):
        app.session.remove()

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        app.logger.error(f"Encountered unhandled error: {error}")
        traceback.print_exc()
        return {"message": str(error).split('\n', 1)[0]}, 500

    return app


def create_scheduler(app):
    # Make sure we run just once in debug mode
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        sched = BackgroundScheduler()
        if app.config.get('run_rules'):
            sched.add_job(
                func=convertor_helper.periodic_work_assignment,
                args=[app],
                trigger="interval",
                minutes=app.config.get('periodic_work_assignment_interval'),
                next_run_time=(datetime.now() + timedelta(seconds=20))
            )
        if app.config.get('get_states'):
            sched.add_job(
                func=convertor_helper.get_zombie_screenshots,
                args=[app],
                trigger="interval",
                minutes=app.config.get('get_zombie_screenshot_interval'),
                next_run_time=(datetime.now() + timedelta(seconds=30))
            )
        sched.add_job(
            func=convertor_helper.fail_stuck_work,
            args=[app],
            trigger="interval",
            minutes=app.config.get('pending_work_interval'),
            next_run_time=(datetime.now() + timedelta(seconds=40))
        )
        sched.add_job(
            func=convertor_helper.mark_zombies,
            args=[app],
            trigger="interval",
            minutes=app.config.get('mark_zombie_interval'),
            next_run_time=(datetime.now() + timedelta(seconds=90))
        )
        sched.add_job(
            work_handler.get_work_assignment,
            args=[app],
            trigger="interval",
            seconds=app.config.get('check_work_interval'),
            max_instances=app.config.get('max_parallel_work')
        )
        sched.start()
        logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)


def create_db(app, engine, session):
    local_session = session()
    creds_base.metadata.create_all(bind=engine)
    device_base.metadata.create_all(bind=engine)
    action_base.metadata.create_all(bind=engine)
    state_base.metadata.create_all(bind=engine)
    execution_base.metadata.create_all(bind=engine)
    work_base.metadata.create_all(bind=engine)
    rule_base.metadata.create_all(bind=engine)

    engine.execute(f"INSERT INTO {db_helper.SCHEMA}.rule_order (NAME) SELECT 'rule_order' WHERE NOT EXISTS (SELECT * FROM {db_helper.SCHEMA}.rule_order)")
    engine.execute(f"INSERT OR IGNORE INTO {db_helper.SCHEMA}.action (name, action_type, action_data, last_updated, created_at) VALUES ('screenshot', 'screenshot', 'screenshot', '2021-05-13 10:31:58.380707', '2021-05-13 10:31:58.380707')")

    local_session.commit()
    local_session.close()

    app.session = scoped_session(session, scopefunc=_app_ctx_stack.__ident_func__)


if __name__ == '__main__':
    configure_logging()
    app = create_app()
    configure_app(app)
    create_scheduler(app)
    engine, session = db_helper.get_db(app.config['db_path'])
    create_db(app, engine, session)
    app.run(
        port=app.config.get('port'),
        host=app.config.get('host')
    )
