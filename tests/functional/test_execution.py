

def test_execution_report_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/execution/', headers=headers, json=test_data['execution'])
    assert response.status_code == 200

    execution = response.json['execution']
    assert execution['execution_id'] == test_data['execution']['execution_id']
    assert execution['work_id'] == test_data['execution']['work_id']
    assert execution['state_id'] == test_data['execution']['state_id']
    assert execution['action_name'] == test_data['execution']['action_name']
    assert execution['trigger'] == test_data['execution']['trigger']
    assert execution['status'] == test_data['execution']['status']
    assert execution['run_data'] == test_data['execution']['run_data']
    assert execution['elapsed_time'] == test_data['execution']['elapsed_time']


def test_execution_report_endpoint_no_state_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    test_data['execution']['state_id'] = None
    response = client.post('/api/v1/execution/', headers=headers, json=test_data['execution'])
    assert response.status_code == 200

    execution = response.json['execution']
    assert execution['execution_id'] == test_data['execution']['execution_id']
    assert execution['work_id'] == test_data['execution']['work_id']
    assert execution['state_id'] is None
    assert execution['action_name'] == test_data['execution']['action_name']
    assert execution['trigger'] == test_data['execution']['trigger']
    assert execution['status'] == test_data['execution']['status']
    assert execution['run_data'] == test_data['execution']['run_data']
    assert execution['elapsed_time'] == test_data['execution']['elapsed_time']


def test_execution_report_endpoint_expect_work_not_found(client, headers, test_data):
    response = client.post('/api/v1/execution/', headers=headers, json=test_data['execution'])
    assert response.status_code == 422
    assert response.json['message'] == f"Work with id '{test_data['execution']['work_id']}' was not found"


def test_execution_report_endpoint_expect_state_not_found(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/execution/', headers=headers, json=test_data['execution'])
    assert response.status_code == 422
    assert response.json['message'] == f"State with id '{test_data['execution']['state_id']}' was not found"


def test_execution_all_by_work_id_endpoint_expect_success(client):
    response = client.get('/api/v1/execution/all/by-work-id?id=1')
    assert response.status_code == 200
    assert type(response.json['executions']) is list
