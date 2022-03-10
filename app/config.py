import os
import yaml
from logging.config import dictConfig


class BaseConfig(object):
    ERROR_404_HELP = False


class Development(BaseConfig):
    DEBUG = True
    TESTING = False
    ENV = 'dev'


class Production(BaseConfig):
    DEBUG = False
    TESTING = False
    ENV = 'prod'


config = {
    'development': 'config.Development',
    'production': 'config.Production'
}


def configure_app(app):
    app.config.from_object(config[os.getenv('APP_ENV', 'production')])
    add_server_config(app)


def add_server_config(app):
    config_file_location = os.getenv('SERVER_CONFIG_PATH', '/etc/vaxiin-server-config/config.yaml')
    server_config = {}
    try:
        with open(config_file_location) as file:
            server_config = yaml.full_load(file)
    except FileNotFoundError:
        print(f"Failed to find configuration file at '{config_file_location}', using defaults...")

    app.config['host'] = server_config.get('host', '0.0.0.0')
    app.config['port'] = server_config.get('port', 5000)
    app.config['db_path'] = server_config.get('db_path', '/db')
    app.config['automatic_recovery'] = server_config.get('automatic_recovery', False)
    app.config['match_open_states_interval'] = server_config.get('match_open_states_interval', 300)
    app.config['get_zombie_screenshot_interval'] = server_config.get('get_zombie_screenshot_interval', 300)
    app.config['retry_rule_interval'] = server_config.get('retry_rule_interval', 60)
    app.config['update_state_interval'] = server_config.get('update_state_interval', 60)
    app.config['pending_work_interval'] = server_config.get('pending_work_interval', 10)
    app.config['pending_work_timeout'] = server_config.get('pending_work_timeout', 30)
    app.config['become_zombie_interval'] = server_config.get('become_zombie_interval', 120)
    app.config['mark_zombie_interval'] = server_config.get('mark_zombie_interval', 10)


def configure_logging():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': os.getenv('APP_LOG_LEVEL', 'INFO'),
            'handlers': ['wsgi']
        }
    })
