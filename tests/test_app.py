import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    """Verify root endpoint returns HTTP 200 and version string."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data

def test_health_check(client):
    """
    Session 7 / 10 Gate check:
    Students will deliberately flip this or add `assert False`
    to test CI failure containment.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_api_items(client):
    """Verify items list retrieval and addition."""
    # GET items
    get_res = client.get("/api/items")
    assert get_res.status_code == 200
    assert isinstance(get_res.get_json()["items"], list)

    # POST new item
    post_res = client.post("/api/items", json={"name": "Ansible"})
    assert post_res.status_code == 201