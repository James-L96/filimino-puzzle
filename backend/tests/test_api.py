import pytest

from app import app
from solver import is_valid_complete

VALID_4X4 = [5, 4, 4, 3, 5, 4, 4, 3, 5, 5, 2, 3, 1, 5, 2, 1]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestHealth:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestPuzzleEndpoint:
    def test_returns_puzzle_without_solution(self, client):
        response = client.get("/api/puzzle?size=8&difficulty=easy")
        assert response.status_code == 200
        data = response.get_json()

        assert data["rows"] == 8
        assert data["cols"] == 8
        assert "solution" not in data
        assert isinstance(data["givens"], list)
        assert len(data["givens"]) > 0
        for row, col, value in data["givens"]:
            assert 0 <= row < 8 and 0 <= col < 8
            assert 1 <= value <= 9

    def test_invalid_size_returns_400(self, client):
        response = client.get("/api/puzzle?size=3")
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_invalid_difficulty_returns_400(self, client):
        response = client.get("/api/puzzle?difficulty=nightmare")
        assert response.status_code == 400
        assert "error" in response.get_json()


class TestCheckEndpoint:
    def test_valid_solution_is_solved(self, client):
        response = client.post(
            "/api/check", json={"rows": 4, "cols": 4, "values": VALID_4X4}
        )
        assert response.status_code == 200
        assert response.get_json() == {"solved": True}

    def test_invalid_grid_is_not_solved(self, client):
        values = list(VALID_4X4)
        values[1] = 5  # breaks the 2x2 region of 4s
        response = client.post(
            "/api/check", json={"rows": 4, "cols": 4, "values": values}
        )
        assert response.status_code == 200
        assert response.get_json() == {"solved": False}

    def test_incomplete_grid_is_not_solved(self, client):
        values = list(VALID_4X4)
        values[0] = None
        response = client.post(
            "/api/check", json={"rows": 4, "cols": 4, "values": values}
        )
        assert response.status_code == 200
        assert response.get_json() == {"solved": False}

    def test_wrong_length_returns_400(self, client):
        response = client.post(
            "/api/check", json={"rows": 4, "cols": 4, "values": VALID_4X4[:15]}
        )
        assert response.status_code == 400

    def test_missing_fields_returns_400(self, client):
        response = client.post("/api/check", json={"values": VALID_4X4})
        assert response.status_code == 400


def test_is_valid_complete_matches_check_endpoint(client):
    values = list(VALID_4X4)
    values[2] = 3
    assert is_valid_complete(values, 4, 4) is False
    response = client.post(
        "/api/check", json={"rows": 4, "cols": 4, "values": values}
    )
    assert response.get_json() == {"solved": False}
