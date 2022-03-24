import io
import base64


def test_state_create_endpoint_expect_success(client, headers, test_data):
    response = client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    assert response.status_code == 200

    new_state = response.json['state']
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] == test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['state']['matched_rule']


def test_state_create_endpoint_with_matched_rule_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.get(f"/api/v1/state/?id={test_data['state']['state_id']}")
    assert response.status_code == 200

    new_state = response.json['states'][0]
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] == test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['rule']['name']


def test_state_create_endpoint_updates_existing_unresolved_state_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/all?uid={test_data['device']['uid']}")

    assert response.status_code == 200
    assert len(response.json['states']) == 1
    assert response.json['states'][0]['device_uid'] == test_data['device']['uid']


def test_state_create_endpoint_with_file_expect_success(client, headers, test_data):
    data = {'screenshot': (io.BytesIO(base64.b64decode(test_data['state']['screenshot'].encode('ascii'))), "screenshot.png")}
    response = client.post(f"/api/v1/state/?device_uid={test_data['state']['device_uid']}", data=data)
    assert response.status_code == 200

    new_state = response.json['state']
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] == test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['state']['matched_rule']


def test_state_get_endpoint_expect_success(client, headers, test_data):
    response = client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/?id={test_data['state']['state_id']}")
    assert response.status_code == 200

    new_state = response.json['states'][0]
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] == test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['state']['matched_rule']


def test_state_get_endpoint_expect_not_found(client, test_data):
    response = client.get(f"/api/v1/state/?id={test_data['state']['state_id']}")
    assert response.status_code == 404
    assert response.json['message'] == f"State with id '{test_data['state']['state_id']}' was not found"


def test_state_resolve_by_device_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.post(f"/api/v1/state/resolve?uid={test_data['state']['device_uid']}")
    assert response.status_code == 200

    new_state = response.json['states'][0]
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] is not test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['state']['matched_rule']


def test_state_resolve_by_device_endpoint_expect_not_found(client, test_data):
    response = client.post("/api/v1/state/resolve?uid={test_data['state']['device_uid']}")
    assert response.status_code == 404


def test_state_update_resolve_endpoint_expect_success(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.post("/api/v1/state/update-resolve", headers=headers, json={**test_data['state'], **{'resolved': not test_data['state']['resolved']}})
    assert response.status_code == 200

    new_state = response.json['states'][0]
    assert new_state['state_id'] == test_data['state']['state_id']
    assert new_state['screenshot'] == test_data['state']['screenshot']
    assert new_state['device_uid'] == test_data['state']['device_uid']
    assert new_state['resolved'] is not test_data['state']['resolved']
    assert new_state['matched_rule'] == test_data['state']['matched_rule']


def test_state_update_resolve_endpoint_expect_not_found(client, headers, test_data):
    response = client.post("/api/v1/state/update-resolve", headers=headers, json=test_data['state'])
    assert response.status_code == 404
    assert response.json['message'] == f"State with id '{test_data['state']['state_id']}' was not found"


def test_state_all_endpoint_expect_success(client):
    response = client.get('/api/v1/state/all')
    assert response.status_code == 200
    assert type(response.json['states']) is list


def test_state_all_endpoint_with_type_open_expect_success(client):
    response = client.get('/api/v1/state/all?type=open')
    assert response.status_code == 200
    assert type(response.json['states']) is list


def test_state_all_endpoint_with_type_unknown_expect_success(client):
    response = client.get('/api/v1/state/all?type=unknown')
    assert response.status_code == 200
    assert type(response.json['states']) is list


def test_state_all_endpoint_with_type_resolved_expect_success(client):
    response = client.get('/api/v1/state/all?type=resolved')
    assert response.status_code == 200
    assert type(response.json['states']) is list


def test_state_get_all_by_device_uid(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/all?uid={test_data['device']['uid']}")
    assert response.status_code == 200
    assert type(response.json['states']) is list
    assert response.json['states'][0]['device_uid'] == test_data['device']['uid']


def test_state_get_open_by_device_uid(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/all?type=open&uid={test_data['device']['uid']}")
    assert response.status_code == 200
    assert type(response.json['states']) is list
    assert response.json['states'][0]['device_uid'] == test_data['device']['uid']
    assert response.json['states'][0]['resolved'] is False


def test_state_get_resolved_by_device_uid(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post(f"/api/v1/state/resolve?uid={test_data['state']['device_uid']}")
    response = client.get(f"/api/v1/state/all?type=resolved&uid={test_data['device']['uid']}")
    assert response.status_code == 200
    assert type(response.json['states']) is list
    assert response.json['states'][0]['device_uid'] == test_data['device']['uid']
    assert response.json['states'][0]['resolved'] is True


def test_state_get_unknown_by_device_uid(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/all?type=unknown&uid={test_data['device']['uid']}")
    assert response.status_code == 200
    assert type(response.json['states']) is list
    assert response.json['states'][0]['device_uid'] == test_data['device']['uid']
    assert response.json['states'][0]['resolved'] is False
    assert response.json['states'][0]['matched_rule'] is None


def test_state_get_all_by_regex(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.get(f"/api/v1/state/all?regex={test_data['rule']['regex']}")
    assert response.status_code == 200
    assert type(response.json['states']) is list
    assert response.json['states'][0]['state_id'] == test_data['state']['state_id']
