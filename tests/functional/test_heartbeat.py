

def test_heartbeat_endpoint_for_new_device_expect_success(client, headers, test_data):
    response = client.put('/api/v1/heartbeat/', headers=headers, json=test_data['heartbeat'])
    assert response.status_code == 200
    assert response.json['message'] == "OK"


def test_heartbeat_endpoint_for_existing_device_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.put('/api/v1/heartbeat/', headers=headers, json=test_data['heartbeat'])
    assert response.status_code == 200
    assert response.json['message'] == "OK"


def test_heartbeat_endpoint_expect_creds_warning(client, headers, test_data):
    response = client.put('/api/v1/heartbeat/', headers=headers, json={**test_data['heartbeat'], **{'creds_name': 'test creds'}})
    assert response.status_code == 211
    assert response.json['message'] == "Provided creds name was not found, omitted it from update"
