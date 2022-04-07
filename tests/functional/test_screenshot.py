

def test_state_screenshot_by_id_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/screenshot/by-id?id={test_data['state']['state_id']}")
    assert response.status_code == 200
    assert response.content_type == 'image/png'


def test_state_screenshot_by_id_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/screenshot/by-id?id={test_data['state']['state_id']}")
    assert response.status_code == 404
    assert response.json['message'] == f"State with id '{test_data['state']['state_id']}' was not found"


def test_state_screenshot_by_uid_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/screenshot/by-device?uid={test_data['state']['device_uid']}")
    assert response.status_code == 200
    assert response.content_type == 'image/png'


def test_state_screenshot_by_uid_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/screenshot/by-device?uid={test_data['state']['device_uid']}")
    assert response.status_code == 404
    assert response.json['message'] == f"State for device with uid '{test_data['state']['device_uid']}' was not found"


def test_state_screenshot_by_rule_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'screenshot': test_data['state']['screenshot']}})
    response = client.get(f"/api/v1/screenshot/by-rule?name={test_data['rule']['name']}")
    assert response.status_code == 200
    assert response.content_type == 'image/png'


def test_state_screenshot_by_rule_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/screenshot/by-rule?name={test_data['rule']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Rule with name '{test_data['rule']['name']}' was not found"
