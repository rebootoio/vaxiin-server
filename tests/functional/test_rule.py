

def test_rule_create_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['state_id'] == test_data['rule']['state_id']
    assert new_rule['regex'] == test_data['rule']['regex']
    assert new_rule['actions'] == test_data['rule']['actions']
    assert new_rule['ignore_case'] == test_data['rule']['ignore_case']
    assert new_rule['enabled'] == test_data['rule']['enabled']


def test_rule_create_endpoint_expect_both_order_attr_cannot_be_set(client, headers, test_data):
    response = client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'before_rule': 'rule', 'after_rule': 'rule'}})
    assert response.status_code == 409
    assert response.json['message'] == "Please set either 'before_rule' OR 'after_rule'"


def test_rule_create_endpoint_expect_regex_is_not_valid(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    invalid_regex = 'he['
    invalid_regex_error = 'unterminated character set at position 2'
    response = client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'regex': invalid_regex}})
    assert response.status_code == 422
    assert response.json['message'] == f"Regex '{invalid_regex}' is invalid, error is: '{invalid_regex_error}'"


def test_rule_create_endpoint_expect_action_not_found(client, headers, test_data):
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 422
    assert response.json['message'] == f"Action with name '{test_data['action']['name']}' was not found"


def test_rule_create_endpoint_expect_state_not_found(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 422
    assert response.json['message'] == f"State with id '{test_data['state']['state_id']}' was not found"


def test_rule_create_endpoint_expect_already_exist(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 409
    assert response.json['message'] == f"Rule with name '{test_data['rule']['name']}' already exist"


def test_rule_update_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'ignore_case': False}})
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['state_id'] == test_data['rule']['state_id']
    assert new_rule['regex'] == test_data['rule']['regex']
    assert new_rule['actions'] == test_data['rule']['actions']
    assert new_rule['ignore_case'] is False
    assert new_rule['enabled'] == test_data['rule']['enabled']


def test_rule_update_endpoint_expect_both_order_attr_cannot_be_set(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'before_rule': 'rule', 'after_rule': 'rule'}})
    assert response.status_code == 409
    assert response.json['message'] == "Please set either 'before_rule' OR 'after_rule'"


def test_rule_update_endpoint_expect_regex_is_not_valid(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    invalid_regex = 'he['
    invalid_regex_error = 'unterminated character set at position 2'
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'regex': invalid_regex}})
    assert response.status_code == 422
    assert response.json['message'] == f"Regex '{invalid_regex}' is invalid, error is: '{invalid_regex_error}'"


def test_rule_update_endpoint_expect_action_not_found(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    new_action_name = "my new action"
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'actions': [new_action_name]}})
    assert response.status_code == 422
    assert response.json['message'] == f"Action with name '{new_action_name}' was not found"


def test_rule_update_endpoint_expect_state_not_found(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    new_state_id = 2
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'state_id': new_state_id}})
    assert response.status_code == 422
    assert response.json['message'] == f"State with id '{new_state_id}' was not found"


def test_rule_update_endpoint_expect_not_found(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    response = client.put('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 404
    assert response.json['message'] == f"Rule with name '{test_data['rule']['name']}' was not found"


def test_rule_delete_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.delete(f"/api/v1/rule/?name={test_data['rule']['name']}")
    assert response.status_code == 200

    response = client.get(f"/api/v1/rule/?name={test_data['rule']['name']}")
    assert response.status_code == 404


def test_rule_delete_endpoint_expect_not_found(client, headers, test_data):
    response = client.delete(f"/api/v1/rule/?name={test_data['rule']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Rule with name '{test_data['rule']['name']}' was not found"


def test_rule_get_endpoint_expect_success(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    response = client.get(f"/api/v1/rule/?name={test_data['rule']['name']}")
    assert response.status_code == 200

    new_rule = response.json['rules'][0]
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['state_id'] == test_data['rule']['state_id']
    assert new_rule['regex'] == test_data['rule']['regex']
    assert new_rule['actions'] == test_data['rule']['actions']
    assert new_rule['ignore_case'] == test_data['rule']['ignore_case']
    assert new_rule['enabled'] == test_data['rule']['enabled']


def test_rule_get_endpoint_expect_not_found(client, headers, test_data):
    response = client.get(f"/api/v1/rule/?name={test_data['rule']['name']}")
    assert response.status_code == 404
    assert response.json['message'] == f"Rule with name '{test_data['rule']['name']}' was not found"


def test_rule_all_endpoint_expect_success(client):
    response = client.get('/api/v1/rule/all')
    assert response.status_code == 200
    assert type(response.json['rules']) is list


def test_rule_ordered_endpoint_expect_success(client):
    response = client.get('/api/v1/rule/ordered')
    assert response.status_code == 200
    assert type(response.json['rules']) is list


def test_rule_ordered_enabledendpoint_expect_success(client):
    response = client.get('/api/v1/rule/ordered-enabled')
    assert response.status_code == 200
    assert type(response.json['rules']) is list


def test_rule_create_after_in_order(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'name': "test rule 2"}})
    test_data['rule']['after_rule'] = test_data['rule']['name']
    test_data['rule']['name'] = "test rule 3"
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['position'] == 2


def test_rule_create_before_in_order(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    test_data['rule']['before_rule'] = test_data['rule']['name']
    test_data['rule']['name'] = "test rule 2"
    response = client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['position'] == 1


def test_rule_update_after_in_order(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    new_rule_name = "test rule 2"
    client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'name': new_rule_name}})
    test_data['rule']['after_rule'] = new_rule_name
    response = client.put('/api/v1/rule/', headers=headers, json=test_data['rule'])
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == test_data['rule']['name']
    assert new_rule['position'] == 2


def test_rule_update_before_in_order(client, headers, test_data):
    client.post('/api/v1/action/', headers=headers, json=test_data['action'])
    client.put('/api/v1/state/', headers=headers, json=test_data['state'])
    client.post('/api/v1/rule/', headers=headers, json=test_data['rule'])
    new_rule_name = "test rule 2"
    client.post('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'name': new_rule_name}})
    test_data['rule']['before_rule'] = test_data['rule']['name']
    response = client.put('/api/v1/rule/', headers=headers, json={**test_data['rule'], **{'name': new_rule_name}})
    assert response.status_code == 200

    new_rule = response.json['rule']
    assert new_rule['name'] == new_rule_name
    assert new_rule['position'] == 1
