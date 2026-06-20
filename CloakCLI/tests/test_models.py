"""Test Pydantic models deserialization."""

from cloakcli.models import (
    Profile, ProfileCreate, ProfileUpdate, LaunchResult,
    SystemStatus, ProfileStatus, TagCreate,
)


class TestProfileCreate:
    def test_minimal(self):
        m = ProfileCreate(name="test")
        data = m.model_dump(exclude_none=True)
        assert data["name"] == "test"
        assert data.get("proxy") is None

    def test_with_tags(self):
        m = ProfileCreate(name="test", tags=[TagCreate(tag="prod", color="#ff0000")])
        data = m.model_dump(exclude_none=True)
        assert len(data["tags"]) == 1
        assert data["tags"][0]["tag"] == "prod"


class TestProfileUpdate:
    def test_exclude_unset(self):
        m = ProfileUpdate(name="renamed")
        data = m.model_dump(exclude_unset=True)
        assert data == {"name": "renamed"}  # only name

    def test_all_fields_none_by_default(self):
        m = ProfileUpdate()
        assert m.name is None
        assert m.proxy is None


class TestProfile:
    def test_from_response(self):
        data = {
            "id": "abc123",
            "name": "test",
            "fingerprint_seed": 12345,
            "user_data_dir": "/data/profiles/abc123",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
            "tags": [{"tag": "prod", "color": None}],
        }
        p = Profile(**data)
        assert p.id == "abc123"
        assert p.status == "stopped"  # default
        assert len(p.tags) == 1


class TestLaunchResult:
    def test_from_response(self):
        data = {"profile_id": "abc", "vnc_ws_port": 6100, "display": ":100"}
        r = LaunchResult(**data)
        assert r.status == "running"
        assert r.vnc_ws_port == 6100


class TestSystemStatus:
    def test_from_response(self):
        data = {"running_count": 2, "binary_version": "145.0", "profiles_total": 10}
        s = SystemStatus(**data)
        assert s.running_count == 2
