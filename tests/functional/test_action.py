from app.helpers.special_keys import SPECIAL_KEYS


def test_action_create_endpoint_expect_success(client, headers, test_data):
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_data['action']['name']
    assert new_action['action_type'] == test_data['action']['action_type']
    assert new_action['action_data'] == test_data['action']['action_data']


def test_action_with_params_create_endpoint_expect_success(client, headers, test_data):
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action_with_params'])
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_data['action_with_params']['name']
    assert new_action['action_type'] == test_data['action_with_params']['action_type']
    assert new_action['action_data'] == test_data['action_with_params']['action_data']


def test_action_create_endpoint_expect_already_exist(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 409
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' already exist"


def test_action_create_endpoint_with_empty_data_expect_failure(client, headers, test_data):
    test_data['action']['action_data'] = ""
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 400
    assert response.json['errors']['action_data'] == "Must not be empty string"


def test_action_create_endpoint_expect_param_key_error(client, headers, test_data):
    test_data['action']['action_data'] = "{hello::there}"
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param key 'hello' is invalid. Allowed keys: [device, cred, metadata]"


def test_action_create_endpoint_expect_device_param_value_error(client, headers, test_data):
    test_data['action']['action_data'] = "{device::me}"
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param value 'me' is invalid for 'device'. Allowed values: [uid, ipmi_ip, model]"


def test_action_create_endpoint_expect_creds_param_value_error(client, headers, test_data):
    test_data['action']['action_data'] = "{cred::me}"
    response = client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param value 'me' is invalid for 'cred'. Allowed values: [username, password]"


def test_action_update_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    new_action_data = "raw 13"
    response = client.put('/api/v1/action/', headers=headers, json={**test_data['action'], **{'action_data': new_action_data}})
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_data['action']['name']
    assert new_action['action_type'] == test_data['action']['action_type']
    assert new_action['action_data'] == new_action_data


def test_action_with_params_update_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    response = client.put('/api/v1/action/', headers=headers, json={**test_data['action'], **{'action_data': test_data['action_with_params']['action_data']}})
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_data['action']['name']
    assert new_action['action_type'] == test_data['action']['action_type']
    assert new_action['action_data'] == test_data['action_with_params']['action_data']


def test_action_update_endpoint_expect_param_key_error(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['action']['action_data'] = "{hello::there}"
    response = client.put('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param key 'hello' is invalid. Allowed keys: [device, cred, metadata]"


def test_action_update_endpoint_expect_device_param_value_error(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['action']['action_data'] = "{device::me}"
    response = client.put('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param value 'me' is invalid for 'device'. Allowed values: [uid, ipmi_ip, model]"


def test_action_update_endpoint_expect_creds_param_value_error(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    test_data['action']['action_data'] = "{cred::me}"
    response = client.put('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 422
    assert response.json['message'] == "The param value 'me' is invalid for 'cred'. Allowed values: [username, password]"


def test_action_update_endpoint_expect_not_found(client, headers, test_data):
    response = client.put('/api/v1/action/', headers=headers, json=test_data['action'])
    assert response.status_code == 404
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' was not found"


def test_action_delete_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    response = client.delete(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 200

    response = client.get(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 404


def test_action_delete_endpoint_expect_not_found(client, headers, test_data):
    response = client.delete(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' was not found"


def test_action_delete_endpoint_expect_in_use(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.delete(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 409
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' was found in rules '{test_data['rule']['name']}'"


def test_action_get_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    response = client.get(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 200

    new_action = response.json['actions'][0]
    assert new_action['name'] == test_data['action']['name']
    assert new_action['action_type'] == test_data['action']['action_type']
    assert new_action['action_data'] == test_data['action']['action_data']


def test_action_get_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/action/?name={test_data['action']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' was not found"


def test_action_all_endpoint_expect_success(client):
    response = client.get('/api/v1/action/all')
    assert response.status_code == 200
    assert type(response.json['actions']) is list


def test_action_screenshot_exists_expect_success(client):
    # TODO - where should this be?
    response = client.get('/api/v1/action/all')
    action_list = response.json['actions']
    assert len(action_list) == 1
    assert action_list[0]['name'] == 'screenshot'
    assert action_list[0]['action_type'] == 'screenshot'
    assert action_list[0]['action_data'] == 'screenshot'


def test_action_list_types_endpoint_expect_success(client):
    response = client.get('/api/v1/action/list-types')
    assert response.status_code == 200

    action_type_list = response.json['action_types']
    assert action_type_list == ['keystroke', 'ipmitool', 'power', 'sleep', 'request']


def test_action_list_power_options_endpoint_expect_success(client):
    response = client.get('/api/v1/action/list-power-options')
    assert response.status_code == 200

    power_option_list = response.json['power_options']
    assert power_option_list == ['on', 'off', 'reset', 'graceful', 'status']


def test_action_list_special_keys_endpoint_expect_success(client):
    response = client.get('/api/v1/action/list-special-keys')
    assert response.status_code == 200

    special_keys_list = response.json['special_keys']
    assert special_keys_list == SPECIAL_KEYS
