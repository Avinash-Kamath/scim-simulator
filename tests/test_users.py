import json
from unittest.mock import MagicMock, patch

import scim_sim.users as users

CONFIG = {"SCIM_BASE_URL": "https://scim.example.com", "SCIM_AUTH_TOKEN": "token123"}
BASE_URL = CONFIG["SCIM_BASE_URL"]
TOKEN = CONFIG["SCIM_AUTH_TOKEN"]


def make_response(status_code, body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.text = json.dumps(body or {})
    return resp


class TestGenerateRandomPayload:
    def test_has_required_keys(self):
        payload = users.generate_random_payload()
        assert payload["active"] is True
        assert "userName" in payload
        assert "name" in payload
        assert "nickName" in payload
        assert "userType" in payload

    def test_name_subfields(self):
        name = users.generate_random_payload()["name"]
        for field in ("givenName", "familyName", "formatted", "middleName",
                      "honorificPrefix", "honorificSuffix"):
            assert field in name

    def test_username_is_string(self):
        assert isinstance(users.generate_random_payload()["userName"], str)

    def test_returns_different_payloads(self):
        usernames = {users.generate_random_payload()["userName"] for _ in range(5)}
        assert len(usernames) > 1


class TestAddUser:
    def test_success_returns_user_id(self, capsys):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(201, {"id": "u1"})):
            user_id = users.add_user()
        assert user_id == "u1"
        assert "u1" in capsys.readouterr().out

    def test_failure_returns_none(self, capsys):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(400)):
            user_id = users.add_user()
        assert user_id is None
        assert "Failed" in capsys.readouterr().out

    def test_posts_to_correct_url(self):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(201, {"id": "u1"})) as mock_req:
            users.add_user()
        args, _ = mock_req.call_args
        assert args[0] == "POST"
        assert args[1] == f"{BASE_URL}/Users"


class TestRemoveUser:
    def test_success_prints_confirmation(self, capsys):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(204)):
            users.remove_user("u1")
        assert "deleted successfully" in capsys.readouterr().out

    def test_failure_prints_error(self, capsys):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(404)):
            users.remove_user("u1")
        assert "Failed" in capsys.readouterr().out

    def test_calls_correct_url(self):
        with patch.object(users, "ensure_valid_config", return_value=CONFIG), \
             patch.object(users, "make_request", return_value=make_response(204)) as mock_req:
            users.remove_user("u1")
        args, _ = mock_req.call_args
        assert args[0] == "DELETE"
        assert args[1] == f"{BASE_URL}/Users/u1"
