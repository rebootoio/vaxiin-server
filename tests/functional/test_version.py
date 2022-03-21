from app.version import VERSION


def test_version_endpoint_expect_success(client):
    response = client.get('/version/')
    assert response.status_code == 200
    assert response.json['version'] == VERSION
