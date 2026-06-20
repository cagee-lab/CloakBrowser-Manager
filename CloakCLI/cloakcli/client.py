"""SDK client for CloakBrowser Manager REST API."""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config
from .errors import _raise_for_status
from .models import (
    ClipboardRequest,
    LaunchResult,
    Profile,
    ProfileCreate,
    ProfileStatus,
    ProfileUpdate,
    SystemStatus,
)


class ProfileAPI:
    """Profile CRUD operations. Access via client.profiles."""
    def __init__(self, client: CloakBrowserManagerClient):
        self._client = client
        self._http = client._http

    def list(self) -> list[Profile]:
        r = self._http.get("/api/profiles")
        _raise_for_status(r.status_code, r.text)
        return [Profile(**item) for item in r.json()]

    def get(self, profile_id: str) -> Profile:
        r = self._http.get(f"/api/profiles/{profile_id}")
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def create(self, **kwargs: Any) -> Profile:
        body = ProfileCreate(**kwargs).model_dump(exclude_none=True)
        r = self._http.post("/api/profiles", json=body)
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def update(self, profile_id: str, **kwargs: Any) -> Profile:
        body = ProfileUpdate(**kwargs).model_dump(exclude_unset=True)
        r = self._http.put(f"/api/profiles/{profile_id}", json=body)
        _raise_for_status(r.status_code, r.text)
        return Profile(**r.json())

    def delete(self, profile_id: str) -> bool:
        r = self._http.delete(f"/api/profiles/{profile_id}")
        _raise_for_status(r.status_code, r.text)
        return True


class ClipboardAPI:
    """Clipboard read/write. Access via client.clipboard."""
    def __init__(self, client: CloakBrowserManagerClient):
        self._http = client._http

    def read(self, profile_id: str) -> str:
        r = self._http.get(f"/api/profiles/{profile_id}/clipboard")
        _raise_for_status(r.status_code, r.text)
        return r.json().get("text", "")

    def write(self, profile_id: str, text: str) -> None:
        body = ClipboardRequest(text=text).model_dump()
        r = self._http.post(f"/api/profiles/{profile_id}/clipboard", json=body)
        _raise_for_status(r.status_code, r.text)


class CloakBrowserManagerClient:
    """Client for CloakBrowser Manager REST API.

    Usage:
        client = CloakBrowserManagerClient(host="http://localhost:8080", token="secret")
        profiles = client.profiles.list()
        client.launch("profile-id")
    """

    def __init__(
        self,
        host: str = "http://localhost:8080",
        token: str | None = None,
        timeout: float = 30.0,
    ):
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._http = httpx.Client(
            base_url=host.rstrip("/"),
            headers=headers,
            timeout=timeout,
        )
        self.profiles = ProfileAPI(self)
        self.clipboard = ClipboardAPI(self)

    @classmethod
    def from_config(cls, config: Config, timeout: float = 30.0) -> CloakBrowserManagerClient:
        return cls(host=config.host, token=config.token, timeout=timeout)

    def launch(self, profile_id: str) -> LaunchResult:
        r = self._http.post(f"/api/profiles/{profile_id}/launch")
        _raise_for_status(r.status_code, r.text)
        return LaunchResult(**r.json())

    def stop(self, profile_id: str) -> bool:
        r = self._http.post(f"/api/profiles/{profile_id}/stop")
        _raise_for_status(r.status_code, r.text)
        return True

    def status(self, profile_id: str | None = None) -> SystemStatus | ProfileStatus:
        if profile_id is None:
            r = self._http.get("/api/status")
            _raise_for_status(r.status_code, r.text)
            return SystemStatus(**r.json())
        r = self._http.get(f"/api/profiles/{profile_id}/status")
        _raise_for_status(r.status_code, r.text)
        return ProfileStatus(**r.json())

    def close(self) -> None:
        self._http.close()
