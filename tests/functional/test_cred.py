

def test_creds_create_endpoint_expect_success(client, headers, test_data):
    response = client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    assert response.status_code == 200

    new_creds = response.json['creds']
    assert new_creds['name'] == test_data['creds']['name']
    assert new_creds['username'] == test_data['creds']['username']
    assert new_creds['password'] == test_data['creds']['password']


def test_creds_create_endpoint_expect_name_is_reserved(client, headers, test_data):
    reserved_name = "default"
    response = client.post('/api/v1/creds/', headers=headers, json={**test_data['creds'], **{'name': reserved_name}})
    assert response.status_code == 409
    assert response.json['message'] == f"The name '{reserved_name}' is reserved"


def test_creds_create_endpoint_expect_already_exist(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    assert response.status_code == 409
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' already exist"


def test_creds_update_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    new_creds_password = "password 2"
    response = client.put('/api/v1/creds/', headers=headers, json={**test_data['creds'], **{'password': new_creds_password}})
    assert response.status_code == 200

    new_creds = response.json['creds']
    assert new_creds['name'] == test_data['creds']['name']
    assert new_creds['username'] == test_data['creds']['username']
    assert new_creds['password'] == new_creds_password


def test_creds_update_endpoint_expect_name_is_reserved(client, headers, test_data):
    reserved_name = "default"
    response = client.put('/api/v1/creds/', headers=headers, json={**test_data['creds'], **{'name': reserved_name}})
    assert response.status_code == 409
    assert response.json['message'] == f"The name '{reserved_name}' is reserved"


def test_creds_update_endpoint_expect_not_found(client, headers, test_data):
    response = client.put('/api/v1/creds/', headers=headers, json=test_data['creds'])
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' was not found"


def test_creds_delete_endpoint_expect_success(client, headers, test_data):
    delete_creds_name = "test creds 2"
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/creds/', headers=headers, json={**test_data['creds'], **{'name': delete_creds_name}})
    response = client.delete(f"/api/v1/creds/?name={delete_creds_name}")
    assert response.status_code == 200

    response = client.get(f"/api/v1/creds/?name={delete_creds_name}")
    assert response.status_code == 404


def test_creds_delete_endpoint_expect_not_found(client, headers, test_data):
    response = client.delete(f"/api/v1/creds/?name={test_data['creds']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' was not found"


def test_creds_delete_endpoint_expect_set_as_default(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.delete(f"/api/v1/creds/?name={test_data['creds']['name']}")
    assert response.status_code == 409
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' are set as the default"


def test_creds_delete_endpoint_expect_in_use(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    client.post('/api/v1/device/', headers=headers, json=test_data['device'])
    response = client.delete(f"/api/v1/creds/?name={test_data['creds']['name']}")
    assert response.status_code == 409
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' are used in devices '{test_data['device']['uid']}'"


def test_creds_get_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.get(f"/api/v1/creds/?name={test_data['creds']['name']}")
    assert response.status_code == 200

    new_creds = response.json['creds'][0]
    assert new_creds['name'] == test_data['creds']['name']
    assert new_creds['username'] == test_data['creds']['username']
    assert new_creds['password'] == test_data['creds']['password']


def test_creds_get_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/creds/?name={test_data['creds']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' was not found"


def test_creds_all_endpoint(client):
    response = client.get('/api/v1/creds/all')
    assert response.status_code == 200
    assert type(response.json['creds']) is list


def test_creds_set_default_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.put(f"/api/v1/creds/default?name={test_data['creds']['name']}")
    assert response.status_code == 200

    default_creds = response.json['creds']
    assert default_creds['name'] == test_data['creds']['name']
    assert default_creds['username'] == test_data['creds']['username']
    assert default_creds['password'] == test_data['creds']['password']


def test_creds_set_default_endpoint_expect_not_found(client, headers, test_data):
    response = client.put(f"/api/v1/creds/default?name={test_data['creds']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Creds with name '{test_data['creds']['name']}' was not found"


def test_creds_get_default_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/creds/', headers=headers, json=test_data['creds'])
    response = client.get('/api/v1/creds/default')
    assert response.status_code == 200

    default_creds = response.json['creds']
    assert default_creds['name'] == test_data['creds']['name']
    assert default_creds['username'] == test_data['creds']['username']
    assert default_creds['password'] == test_data['creds']['password']


def test_creds_get_default_endpoint_expect_null(client):
    response = client.get('/api/v1/creds/default')
    assert response.status_code == 200
    assert response.json['creds'] is None
