

def test_state_screenshot_by_id_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state-screenshot/by-id?id={test_data['state']['state_id']}")
    assert response.status_code == 200
    assert response.content_type == 'image/png'


def test_state_screenshot_by_id_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/state-screenshot/by-id?id={test_data['state']['state_id']}")
    assert response.status_code == 404
    assert response.json['message'] == f"State with id '{test_data['state']['state_id']}' was not found"


def test_state_screenshot_by_uid_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state-screenshot/by-device?uid={test_data['state']['device_uid']}")
    assert response.status_code == 200
    assert response.content_type == 'image/png'


def test_state_screenshot_by_uid_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/state-screenshot/by-device?uid={test_data['state']['device_uid']}")
    assert response.status_code == 404
    assert response.json['message'] == f"State for device with uid '{test_data['state']['device_uid']}' was not found"
