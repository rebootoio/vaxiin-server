import pytest


def test_config_default_values(app):
    assert app.config['host'] == '0.0.0.0'
    assert app.config['port'] == 5000
    assert app.config['db_path'] == '/db'
    assert app.config['get_states'] is True
    assert app.config['run_rules'] is False
    assert app.config['periodic_work_assignment_interval'] == 300
    assert app.config['get_zombie_screenshot_interval'] == 300
    assert app.config['retry_rule_interval'] == 60
    assert app.config['update_state_interval'] == 60
    assert app.config['pending_work_interval'] == 10
    assert app.config['pending_work_timeout'] == 30
    assert app.config['become_zombie_interval'] == 120
    assert app.config['mark_zombie_interval'] == 10


@pytest.mark.parametrize("app", [True], indirect=True)
def test_config_values_from_yaml(app):
    assert app.config['host'] == '127.0.0.1'
    assert app.config['port'] == 5000
    assert app.config['db_path'] == './'
    assert app.config['get_states'] is False
    assert app.config['run_rules'] is True
    assert app.config['periodic_work_assignment_interval'] == 3
    assert app.config['get_zombie_screenshot_interval'] == 3
    assert app.config['retry_rule_interval'] == 10
    assert app.config['update_state_interval'] == 10
    assert app.config['pending_work_interval'] == 1
    assert app.config['pending_work_timeout'] == 5
    assert app.config['become_zombie_interval'] == 5
    assert app.config['mark_zombie_interval'] == 1
