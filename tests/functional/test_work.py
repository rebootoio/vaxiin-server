

def test_work_create_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 200

    new_work = response.json['work']
    assert new_work['device_uid'] == test_data['device']['uid']
    assert new_work['actions'][0]['name'] == test_data['action']['name']
    assert new_work['trigger'] == f"Manual - Rule: {test_data['rule']['name']}"


def test_work_create_endpoint_no_rule_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 200

    new_work = response.json['work']
    assert new_work['device_uid'] == test_data['device']['uid']
    assert new_work['actions'][0]['name'] == test_data['action']['name']
    assert new_work['trigger'] == f"Manual - Actions: {test_data['action']['name']}"


def test_work_create_endpoint_expect_already_exist(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 409
    assert response.json['message'] == f"Device '{test_data['device']['uid']}' already has pending work"


def test_work_create_endpoint_expect_device_not_found(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 422
    assert response.json['message'] == f"Device with uid '{test_data['work']['device_uid']}' was not found"


def test_work_create_endpoint_expect_action_not_found(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    test_data['work'].pop('rule')
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 422
    assert response.json['message'] == f"Action with name '{test_data['work']['actions'][0]}' was not found"


def test_work_create_endpoint_expect_rule_not_found(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 422
    assert response.json['message'] == f"Rule with name '{test_data['work']['rule']}' was not found"


def test_work_create_endpoint_expect_requires_rule_or_action(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    test_data['work'].pop('rule')
    test_data['work'].pop('actions')
    response = client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    assert response.status_code == 422
    assert response.json['message'] == "Either 'rule' or 'actions' must be set for work"


def test_work_assign_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200

    assignment = response.json['assignment']
    assert assignment['work_id'] == test_data['work']['work_id']
    assert assignment['state_id'] is None
    assert assignment['trigger'] == f"Manual - Actions: {test_data['action']['name']}"
    assert assignment['action_list'][0]['name'] == test_data['action']['name']
    assert assignment['action_list'][0]['type'] == test_data['action']['action_type']
    assert assignment['action_list'][0]['data'] == test_data['action']['action_data']
    assert assignment['device_data']['uid'] == test_data['device']['uid']
    assert assignment['device_data']['ip'] == test_data['device']['ipmi_ip']
    assert assignment['device_data']['model'] == test_data['device']['model']
    assert assignment['device_data']['username'] == test_data['creds']['username']
    assert assignment['device_data']['password'] == test_data['creds']['password']


def test_work_assign_endpoint_with_params_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action_with_params'])
    test_data['work'].pop('rule')
    test_data['work']['actions'] = [test_data['action_with_params']['name']]
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200

    assignment = response.json['assignment']
    assert assignment['work_id'] == test_data['work']['work_id']
    assert assignment['state_id'] is None
    assert assignment['trigger'] == f"Manual - Actions: {test_data['action_with_params']['name']}"
    assert assignment['action_list'][0]['name'] == test_data['action_with_params']['name']
    assert assignment['action_list'][0]['type'] == test_data['action_with_params']['action_type']
    device_data = test_data['device']
    creds_data = test_data['creds']
    assert assignment['action_list'][0]['data'] == "{myparam} " + f"{device_data['model']} {device_data['ipmi_ip']} {device_data['uid']} {creds_data['username']} {creds_data['password']} {device_data['metadata']['hostname']} {creds_data['username']} {creds_data['password']}"
    assert assignment['device_data']['uid'] == test_data['device']['uid']
    assert assignment['device_data']['ip'] == test_data['device']['ipmi_ip']
    assert assignment['device_data']['model'] == test_data['device']['model']
    assert assignment['device_data']['username'] == test_data['creds']['username']
    assert assignment['device_data']['password'] == test_data['creds']['password']


def test_work_assign_endpoint_with_missing_metadata_expect_work_failure(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json={**test_data['device'], **{'metadata': {}}})
    client.post('/api/v1/action/', headers=headers, json=test_data['action_with_params'])
    test_data['work'].pop('rule')
    test_data['work']['actions'] = [test_data['action_with_params']['name']]
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200
    assert response.json['assignment'] is None

    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200
    assert response.json['works'][0]['status'] == "failure"

    response = client.get(f"/api/v1/execution/all/by-work-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200

    execution_data = response.json['executions'][0]
    assert execution_data['action_name'] == "Missing metadata key"
    assert execution_data['status'] == "failure"
    assert execution_data['run_data'] == f"Action '{test_data['action_with_params']['name']}' requires the metadata key '{list(test_data['device']['metadata'].keys())[0]}' but it is not defined on the device"


def test_work_assign_endpoint_with_missing_cred_from_store_expect_work_failure(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json={**test_data['device'], **{'metadata': {}}})
    test_data['action_with_params']['action_data'] = "fail {cred_store::missing cred::username}"
    client.post('/api/v1/action/', headers=headers, json=test_data['action_with_params'])
    test_data['work'].pop('rule')
    test_data['work']['actions'] = [test_data['action_with_params']['name']]
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200
    assert response.json['assignment'] is None

    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200
    assert response.json['works'][0]['status'] == "failure"

    response = client.get(f"/api/v1/execution/all/by-work-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200

    execution_data = response.json['executions'][0]
    assert execution_data['action_name'] == "Missing cred from store"
    assert execution_data['status'] == "failure"
    assert execution_data['run_data'] == f"Action '{test_data['action_with_params']['name']}' requires the cred 'missing cred' but it was not found"


def test_work_assign_endpoint_expect_null(client):
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200
    assert response.json['assignment'] is None


def test_work_complete_by_id_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/by-id', headers=headers, json={'work_id': test_data['work']['work_id'], 'status': 'success'})
    assert response.status_code == 200

    completed_work = response.json['work']
    assert completed_work['device_uid'] == test_data['device']['uid']
    assert completed_work['actions'][0]['name'] == test_data['action']['name']
    assert completed_work['trigger'] == f"Manual - Actions: {test_data['action']['name']}"
    assert completed_work['assigned'] is None
    assert completed_work['status'] == "success"


def test_work_complete_by_id_endpoint_expect_not_found(client, headers, test_data):
    response = client.post('/api/v1/work/by-id', headers=headers, json={'work_id': test_data['work']['work_id'], 'status': 'success'})
    assert response.status_code == 404
    assert response.json['message'] == f"Work with id '{test_data['work']['work_id']}' was not found"


def test_work_complete_by_id_endpoint_expect_not_pending(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    client.post('/api/v1/work/by-id', headers=headers, json={'work_id': test_data['work']['work_id'], 'status': 'success'})
    response = client.post('/api/v1/work/by-id', headers=headers, json={'work_id': test_data['work']['work_id'], 'status': 'success'})
    assert response.status_code == 422
    assert response.json['message'] == f"Work with id '{test_data['work']['work_id']}' is not pending"


def test_work_get_by_id_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 200

    work = response.json['works'][0]
    assert work['device_uid'] == test_data['device']['uid']
    assert work['actions'][0]['name'] == test_data['action']['name']
    assert work['trigger'] == f"Manual - Actions: {test_data['action']['name']}"
    assert work['status'] == "PENDING"


def test_work_get_by_id_endpoint_expect_not_found(client, test_data):
    response = client.get(f"/api/v1/work/by-id?id={test_data['work']['work_id']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Work with id '{test_data['work']['work_id']}' was not found"


def test_work_get_by_device_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.get(f"/api/v1/work/by-device?uid={test_data['device']['uid']}")
    assert response.status_code == 200

    work = response.json['works'][0]
    assert work['device_uid'] == test_data['device']['uid']
    assert work['actions'][0]['name'] == test_data['action']['name']
    assert work['trigger'] == f"Manual - Actions: {test_data['action']['name']}"
    assert work['status'] == "PENDING"


def test_work_get_by_device_endpoint_expect_not_found(client, test_data):
    response = client.get(f"/api/v1/work/by-device?uid={test_data['device']['uid']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Work for device with uid '{test_data['device']['uid']}' was not found"


def test_work_all_endpoint_expect_success(client):
    response = client.get('/api/v1/work/all')
    assert response.status_code == 200
    assert type(response.json['works']) is list


def test_work_all_by_device_endpoint_expect_success(client):
    response = client.get('/api/v1/work/all/by-device?uid=uid')
    assert response.status_code == 200
    assert type(response.json['works']) is list


def test_work_pending_by_device_endpoint_expect_success(client):
    response = client.get('/api/v1/work/pending')
    assert response.status_code == 200
    assert type(response.json['works']) is list


def test_work_completed_by_device_endpoint_expect_success(client):
    response = client.get('/api/v1/work/completed')
    assert response.status_code == 200
    assert type(response.json['works']) is list


def test_get_assignment_with_default_creds(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    test_data['device'].pop('creds_name')
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200

    assignment = response.json['assignment']
    assert assignment['work_id'] == test_data['work']['work_id']
    assert assignment['state_id'] is None
    assert assignment['trigger'] == f"Manual - Actions: {test_data['action']['name']}"
    assert assignment['action_list'][0]['name'] == test_data['action']['name']
    assert assignment['action_list'][0]['type'] == test_data['action']['action_type']
    assert assignment['action_list'][0]['data'] == test_data['action']['action_data']
    assert assignment['device_data']['uid'] == test_data['device']['uid']
    assert assignment['device_data']['ip'] == test_data['device']['ipmi_ip']
    assert assignment['device_data']['model'] == test_data['device']['model']
    assert assignment['device_data']['username'] == test_data['creds']['username']
    assert assignment['device_data']['password'] == test_data['creds']['password']


def test_get_assignment_with_no_default_creds(client, headers, test_data):
    test_data['device'].pop('creds_name')
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['work'].pop('rule')
    client.post('/api/v1/work/', headers=headers, json=test_data['work'])
    response = client.post('/api/v1/work/assign')
    assert response.status_code == 200
    assert response.json['assignment'] is None
