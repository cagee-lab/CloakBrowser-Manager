"""Test CloakBrowserManagerClient with mocked httpx."""

import pytest
import httpx
from cloakcli.client import CloakBrowserManagerClient
from cloakcli.errors import AuthenticationError, NotFoundError


@pytest.fixture
def client():
    """Create a client with mocked transport."""
    client = CloakBrowserManagerClient(host="http://test:8080", token="test-token")
    return client


class TestProfiles:
    def test_list(self, client, httpx_mock):
        httpx_mock.add_response(
            url="http://test:8080/api/profiles",
            json=[
                {"id": "1", "name": "p1", "fingerprint_seed": 1, "user_data_dir": "/d",
                 "created_at": "", "updated_at": ""},
            ],
        )
        profiles = client.profiles.list()
        assert len(profiles) == 1
        assert profiles[0].name == "p1"

    def test_get_not_found(self, client, httpx_mock):
        httpx_mock.add_response(
            url="http://test:8080/api/profiles/missing",
            status_code=404,
            json={"detail": "Not found"},
        )
        with pytest.raises(NotFoundError):
            client.profiles.get("missing")

    def test_create(self, client, httpx_mock):
        httpx_mock.add_response(
            url="http://test:8080/api/profiles",
            status_code=201,
            json={
                "id": "new", "name": "created", "fingerprint_seed": 99,
                "user_data_dir": "/d", "created_at": "", "updated_at": "",
            },
        )
        p = client.profiles.create(name="created")
        assert p.id == "new"

    def test_delete(self, client, httpx_mock):
        httpx_mock.add_response(
            method="DELETE",
            url="http://test:8080/api/profiles/1",
            json={"ok": True},
        )
        assert client.profiles.delete("1") is True


class TestLifecycle:
    def test_launch(self, client, httpx_mock):
        httpx_mock.add_response(
            method="POST",
            url="http://test:8080/api/profiles/1/launch",
            json={
                "profile_id": "1", "vnc_ws_port": 6100, "display": ":100",
            },
        )
        r = client.launch("1")
        assert r.profile_id == "1"
        assert r.vnc_ws_port == 6100

    def test_stop(self, client, httpx_mock):
        httpx_mock.add_response(
            method="POST",
            url="http://test:8080/api/profiles/1/stop",
            json={"ok": True},
        )
        assert client.stop("1") is True


class TestAuth:
    def test_bearer_token_in_header(self, client, httpx_mock):
        httpx_mock.add_response(
            url="http://test:8080/api/profiles",
            json=[],
        )
        client.profiles.list()
        request = httpx_mock.get_request(url="http://test:8080/api/profiles")
        assert request.headers["Authorization"] == "Bearer test-token"

    def test_no_token(self, httpx_mock):
        client = CloakBrowserManagerClient(host="http://test:8080", token=None)
        httpx_mock.add_response(
            url="http://test:8080/api/profiles",
            json=[],
        )
        client.profiles.list()
        request = httpx_mock.get_request(url="http://test:8080/api/profiles")
        assert "Authorization" not in request.headers

    def test_401_raises_auth_error(self, client, httpx_mock):
        httpx_mock.add_response(
            url="http://test:8080/api/profiles",
            status_code=401,
            json={"detail": "Unauthorized"},
        )
        with pytest.raises(AuthenticationError):
            client.profiles.list()
