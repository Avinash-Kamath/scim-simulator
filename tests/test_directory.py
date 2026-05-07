import json
from unittest.mock import MagicMock, patch

import scim_sim.directory as directory

CONFIG = {"SCIM_BASE_URL": "https://scim.example.com", "SCIM_AUTH_TOKEN": "token123"}


def make_response(status_code, body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.text = json.dumps(body or {})
    return resp


GROUPS = {"Resources": [{"id": "grp-1", "displayName": "Engineering"}]}
USERS = {"Resources": [
    {"id": "u1", "userName": "alice@example.com"},
    {"id": "u2", "userName": "bob@example.com"},
]}
GROUP_DETAIL_WITH_U1 = {"id": "grp-1", "displayName": "Engineering", "members": [{"value": "u1"}]}
GROUP_DETAIL_EMPTY = {"id": "grp-1", "displayName": "Engineering", "members": []}


class TestShowDirectory:
    def test_shows_groups_and_users(self, capsys):
        with patch.object(directory, "ensure_valid_config", return_value=CONFIG), \
             patch.object(directory, "make_request", side_effect=[
                 make_response(200, GROUPS),
                 make_response(200, USERS),
                 make_response(200, GROUP_DETAIL_WITH_U1),
             ]):
            directory.show_directory()
        out = capsys.readouterr().out
        assert "Engineering" in out
        assert "alice@example.com" in out
        assert "bob@example.com" in out  # ungrouped

    def test_empty_directory(self, capsys):
        with patch.object(directory, "ensure_valid_config", return_value=CONFIG), \
             patch.object(directory, "make_request", side_effect=[
                 make_response(200, {"Resources": []}),
                 make_response(200, {"Resources": []}),
             ]):
            directory.show_directory()
        assert "empty" in capsys.readouterr().out

    def test_failure_fetching_groups(self, capsys):
        with patch.object(directory, "ensure_valid_config", return_value=CONFIG), \
             patch.object(directory, "make_request", side_effect=[
                 make_response(500),
                 make_response(200, USERS),
             ]):
            directory.show_directory()
        assert "Failed" in capsys.readouterr().out

    def test_failure_fetching_users(self, capsys):
        with patch.object(directory, "ensure_valid_config", return_value=CONFIG), \
             patch.object(directory, "make_request", side_effect=[
                 make_response(200, GROUPS),
                 make_response(500),
             ]):
            directory.show_directory()
        assert "Failed" in capsys.readouterr().out

    def test_ungrouped_users_shown_separately(self, capsys):
        with patch.object(directory, "ensure_valid_config", return_value=CONFIG), \
             patch.object(directory, "make_request", side_effect=[
                 make_response(200, GROUPS),
                 make_response(200, USERS),
                 make_response(200, GROUP_DETAIL_WITH_U1),  # only u1 in group
             ]):
            directory.show_directory()
        out = capsys.readouterr().out
        assert "Ungrouped" in out
        assert "bob@example.com" in out
