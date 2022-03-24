from freezegun import freeze_time
from datetime import datetime, timedelta

import app.helpers.convertor as convertor_helper


def test_fail_stuck_work(app, client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])

    with freeze_time(datetime.now() - timedelta(hours=1)):
        client.post('/api/v1/work/assign')

    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200
    assert response.json['works'][0]['status'] == 'PENDING'
    assert response.json['works'][0]['assigned'] is not None

    convertor_helper.fail_stuck_work(app)
    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200
    assert response.json['works'][0]['status'] == 'failure'
    assert response.json['works'][0]['assigned'] is not None

    response = client.get(f"/api/v1/execution/all/by-work-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200
    assert len(response.json['executions']) == 1

    execution_data = response.json['executions'][0]
    assert execution_data['action_name'] == 'Timeout Exceeded'
    assert execution_data['status'] == 'failure'
    assert execution_data['run_data']['message'] == 'Got a timeout while waiting for assigned work to complete'


def test_periodic_work_assignment(app, client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    convertor_helper.periodic_work_assignment(app)
    # Make sure it does not create another work
    convertor_helper.periodic_work_assignment(app)
    response = client.get(f"/api/v1/work/by-device?uid={test_data['device']['uid']}")
    assert response.status_code == 200
    assert len(response.json['works']) == 1

    work_data = response.json['works'][0]
    assert work_data['status'] == 'PENDING'
    assert work_data['device_uid'] == test_data['device']['uid']
    assert work_data['trigger'] == f"Rule - {test_data['rule']['name']}"


def test_get_zombie_screenshot(app, client, headers, test_data):
    test_data['heartbeat']['heartbeat_timestamp'] = (datetime.now() - timedelta(hours=3)).isoformat()
    client.put('/api/v1/heartbeat/', headers=headers, json=test_data['heartbeat'])
    convertor_helper.mark_zombies(app)
    convertor_helper.get_zombie_screenshots(app)
    # Make sure it does not create another work
    convertor_helper.get_zombie_screenshots(app)
    response = client.get(f"/api/v1/work/by-device?uid={test_data['heartbeat']['uid']}")
    assert response.status_code == 200
    assert len(response.json['works']) == 1

    work_data = response.json['works'][0]
    assert work_data['status'] == 'PENDING'
    assert work_data['device_uid'] == test_data['heartbeat']['uid']
    assert work_data['trigger'] == 'zombie screenshot'
    assert work_data['requires_console'] is True
    assert len(work_data['actions']) == 1
    assert work_data['actions'][0] == {
        'name': 'screenshot',
        'type': 'screenshot',
        'data': 'screenshot'
    }


def test_mark_zombies(app, client, headers, test_data):
    test_data['heartbeat']['heartbeat_timestamp'] = (datetime.now() - timedelta(hours=3)).isoformat()
    client.put('/api/v1/heartbeat/', headers=headers, json=test_data['heartbeat'])
    response = client.get(f"/api/v1/device/?uid={test_data['heartbeat']['uid']}")
    assert response.json['devices'][0]['zombie'] is False

    convertor_helper.mark_zombies(app)
    response = client.get(f"/api/v1/device/?uid={test_data['heartbeat']['uid']}")
    assert response.json['devices'][0]['zombie'] is True
