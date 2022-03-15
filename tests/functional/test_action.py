from app.helpers.special_keys import SPECIAL_KEYS


headers = {
    'Content-Type': 'application/json'
}

test_action = {
    "name": "test action",
    "action_type": "ipmitool",
    "action_data": "lan print"
}


def test_action_create_endpoint(client):
    response = client.post('/api/v1/action/', headers=headers, json=test_action)
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_action['name']
    assert new_action['action_type'] == test_action['action_type']
    assert new_action['action_data'] == test_action['action_data']


def test_action_update_endpoint(client):
    client.post('/api/v1/action/', headers=headers, json=test_action)
    new_action_data = "raw 13"
    response = client.put('/api/v1/action/', headers=headers, json={**test_action, **{'action_data': new_action_data}})
    assert response.status_code == 200

    new_action = response.json['action']
    assert new_action['name'] == test_action['name']
    assert new_action['action_type'] == test_action['action_type']
    assert new_action['action_data'] == new_action_data


def test_action_delete_endpoint(client):
    client.post('/api/v1/action/', headers=headers, json=test_action)
    response = client.delete(f'/api/v1/action/?name={test_action["name"]}')
    assert response.status_code == 200

    response = client.get(f'/api/v1/action/?name={test_action["name"]}')
    assert response.status_code == 404


def test_action_get_endpoint(client):
    client.post('/api/v1/action/', headers=headers, json=test_action)
    response = client.get(f'/api/v1/action/?name={test_action["name"]}')
    assert response.status_code == 200

    new_action = response.json['actions'][0]
    assert new_action['name'] == test_action['name']
    assert new_action['action_type'] == test_action['action_type']
    assert new_action['action_data'] == test_action['action_data']


def test_action_all_endpoint(client):
    response = client.get('/api/v1/action/all')
    assert response.status_code == 200


def test_action_screenshot_exists(client):
    response = client.get('/api/v1/action/all')
    action_list = response.json['actions']
    assert len(action_list) == 1
    assert action_list[0]['name'] == 'screenshot'
    assert action_list[0]['action_type'] == 'screenshot'
    assert action_list[0]['action_data'] == 'screenshot'


def test_action_list_types_endpoint(client):
    response = client.get('/api/v1/action/list-types')
    assert response.status_code == 200

    action_type_list = response.json['action_types']
    assert action_type_list == ['keystroke', 'ipmitool', 'power', 'sleep']


def test_action_list_power_options_endpoint(client):
    response = client.get('/api/v1/action/list-power-options')
    assert response.status_code == 200

    power_option_list = response.json['power_options']
    assert power_option_list == ['on', 'off', 'reset', 'graceful', 'status']


def test_action_list_special_keys_endpoint(client):
    response = client.get('/api/v1/action/list-special-keys')
    assert response.status_code == 200

    special_keys_list = response.json['special_keys']
    assert special_keys_list == SPECIAL_KEYS
