from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_read_extensions():
    response = client.get("/api/extensions")
    assert response.status_code == 200
    assert len(response.json()) == 137


def test_read_extension():
    response = client.get("/api/extensions/150")
    assert response.status_code == 200
    assert response.json() == {
        "extension": "150",
        "name": "Голубкова ЖВ",
        "group_id": "5",
        "title": "Отдел Маркетинга"
    }
    response_short = client.get("/api/extensions/150?short=true")
    assert response_short.status_code == 200
    assert response_short.json() == {
        "extension": "150",
        "name": "Голубкова ЖВ"
    }


def test_read_inexistent_extension():
    response = client.get("/api/extensions/887")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_read_bad_extension():
    response = client.get("/api/extensions/a")
    assert response.status_code == 422


def test_read_groups():
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert len(response.json()) == 8


def test_read_group():
    response = client.get("/api/groups/13")
    assert response.status_code == 200
    assert response.json() == [
        {
            "extension": "124",
            "name": "ОХРАНА",
            "group_id": "13",
            "title": None
        },
        {
            "extension": "103",
            "name": "Устинов АГ",
            "group_id": "13",
            "title": None
        }
    ]


def test_read_inexistent_group():
    response = client.get("/api/groups/84")
    assert response.status_code == 404
    assert response.json() == {"detail": "Group not found"}


def test_read_bad_group():
    response = client.get("/api/groups/x")
    assert response.status_code == 422


# Create

def test_create_group():
    response = client.post("/api/groups/99", json={"title": "Testing"},)
    assert response.status_code == 201
    assert response.json() == {
        "group_id": "99",
        "title": "Testing"
    }


def test_read_groups_plus_one():
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert len(response.json()) == 9


def test_delete_group():
    response = client.delete("/api/groups/99")
    assert response.status_code == 202
    assert response.json() is None


def test_read_groups_minus_one():
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert len(response.json()) == 8
