

def test_device_create_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    assert response.status_code == 200

    new_device = response.json['device']
    assert new_device['uid'] == test_data['device']['uid']
    assert new_device['ipmi_ip'] == test_data['device']['ipmi_ip']
    assert new_device['model'] == test_data['device']['model']
    assert new_device['creds_name'] == test_data['device']['creds_name']
    assert new_device['zombie'] == test_data['device']['zombie']


def test_device_create_endpoint_expect_creds_not_found(client, headers, test_data):
    response = client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' was not found"


def test_device_create_endpoint_expect_already_exist(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    assert response.status_code == 409
    assert response.json['message'] == f"Device with uid '{test_data['device']['uid']}' already exist"


def test_device_update_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    new_device_ipmi_ip = "10.200.33.121"
    response = client.put('/api/v1/device/', headers=headers, json={**test_data['device'], **{'ipmi_ip': new_device_ipmi_ip}})
    assert response.status_code == 200

    new_device = response.json['device']
    assert new_device['uid'] == test_data['device']['uid']
    assert new_device['ipmi_ip'] == new_device_ipmi_ip
    assert new_device['model'] == test_data['device']['model']
    assert new_device['creds_name'] == test_data['device']['creds_name']
    assert new_device['zombie'] == test_data['device']['zombie']


def test_device_update_endpoint_expect_cred_name_not_found(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    new_creds_name = "new creds"
    response = client.put('/api/v1/device/', headers=headers, json={**test_data['device'], **{'creds_name': new_creds_name}})
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{new_creds_name}' was not found"


def test_device_update_endpoint_expect_not_found(client, headers, test_data):
    response = client.put('/api/v1/device/', headers=headers, json=test_data['device'])
    assert response.status_code == 404
    assert response.json['message'] == f"Device with uid '{test_data['device']['uid']}' was not found"


def test_device_delete_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.delete(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 200

    response = client.get(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 404


def test_device_delete_endpoint_expect_not_found(client, headers, test_data):
    response = client.delete(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Device with uid '{test_data['device']['uid']}' was not found"


def test_device_delete_endpoint_expect_in_use(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.delete(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 409
    assert response.json['message'] == f"Device with uid '{test_data['device']['uid']}' has an unresolved state with ID {test_data['state']['state_id']}"


def test_device_get_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.get(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 200

    new_device = response.json['devices'][0]
    assert new_device['uid'] == test_data['device']['uid']
    assert new_device['ipmi_ip'] == test_data['device']['ipmi_ip']
    assert new_device['model'] == test_data['device']['model']
    assert new_device['creds_name'] == test_data['device']['creds_name']
    assert new_device['zombie'] == test_data['device']['zombie']


def test_device_get_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/device/?uid={test_data['device']['uid']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Device with uid '{test_data['device']['uid']}' was not found"


def test_device_all_endpoint_expect_success(client):
    response = client.get('/api/v1/device/all')
    assert response.status_code == 200
    assert type(response.json['devices']) is list


def test_device_zombie_endpoint_expect_success(client):
    response = client.get('/api/v1/device/zombies')
    assert response.status_code == 200
    assert type(response.json['devices']) is list
