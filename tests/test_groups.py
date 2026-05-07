import json
from unittest.mock import MagicMock, patch

import scim_sim.groups as groups

CONFIG = {"SCIM_BASE_URL": "https://scim.example.com", "SCIM_AUTH_TOKEN": "token123"}
BASE_URL = CONFIG["SCIM_BASE_URL"]


def make_response(status_code, body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.text = json.dumps(body or {})
    return resp


class TestGenerateGroupPayload:
    def test_display_name(self):
        assert groups.generate_group_payload("Engineering")["displayName"] == "Engineering"

    def test_members_empty(self):
        assert groups.generate_group_payload("Engineering")["members"] == []


class TestCreateGroup:
    def test_success_returns_group_id(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(201, {"id": "grp-1"})):
            group_id = groups.create_group("Engineering")
        assert group_id == "grp-1"
        assert "grp-1" in capsys.readouterr().out

    def test_failure_returns_none(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(500)):
            group_id = groups.create_group("Engineering")
        assert group_id is None
        assert "Failed" in capsys.readouterr().out

    def test_posts_correct_payload(self):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(201, {"id": "grp-1"})) as mock_req:
            groups.create_group("Engineering")
        _, kwargs = mock_req.call_args
        assert kwargs["json_data"]["displayName"] == "Engineering"
        assert kwargs["json_data"]["members"] == []


class TestDeleteGroup:
    def test_deletes_members_then_group(self, capsys):
        group_body = {"members": [{"value": "u1"}, {"value": "u2"}]}
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, group_body),
                 make_response(204),
             ]), \
             patch.object(groups, "remove_user") as mock_remove:
            groups.delete_group("grp-1")
        mock_remove.assert_any_call("u1")
        mock_remove.assert_any_call("u2")
        assert "deleted successfully" in capsys.readouterr().out

    def test_handles_empty_members(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": []}),
                 make_response(204),
             ]):
            groups.delete_group("grp-1")
        assert "deleted successfully" in capsys.readouterr().out

    def test_handles_null_members_from_api(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": None}),
                 make_response(204),
             ]):
            groups.delete_group("grp-1")
        assert "deleted successfully" in capsys.readouterr().out

    def test_failure_fetching_group(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(404)):
            groups.delete_group("grp-1")
        assert "Failed" in capsys.readouterr().out

    def test_failure_deleting_group(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": []}),
                 make_response(500),
             ]):
            groups.delete_group("grp-1")
        assert "Failed" in capsys.readouterr().out


class TestAddUserToGroup:
    def test_success(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": []}),
                 make_response(200),
             ]):
            result = groups.add_user_to_group("u1", "grp-1")
        assert result is True
        assert "added" in capsys.readouterr().out

    def test_group_not_found(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(404)):
            result = groups.add_user_to_group("u1", "grp-1")
        assert result is False
        assert "not found" in capsys.readouterr().out

    def test_patch_failure(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": []}),
                 make_response(500),
             ]):
            result = groups.add_user_to_group("u1", "grp-1")
        assert result is False
        assert "Failed" in capsys.readouterr().out

    def test_appends_to_existing_members(self):
        existing = [{"value": "existing-user"}]
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": existing}),
                 make_response(200),
             ]) as mock_req:
            groups.add_user_to_group("new-user", "grp-1")
        members_sent = mock_req.call_args_list[1][1]["json_data"]["Operations"][0]["value"]
        assert {"value": "existing-user"} in members_sent
        assert {"value": "new-user"} in members_sent

    def test_handles_null_members_from_api(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, {"members": None}),
                 make_response(200),
             ]):
            result = groups.add_user_to_group("u1", "grp-1")
        assert result is True


class TestRemoveUserFromGroup:
    def test_success(self, capsys):
        group_body = {"members": [{"value": "u1"}, {"value": "u2"}]}
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, group_body),
                 make_response(200),
             ]):
            result = groups.remove_user_from_group("u1", "grp-1")
        assert result is True
        assert "removed" in capsys.readouterr().out

    def test_user_not_in_group(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(200, {"members": [{"value": "u2"}]})):
            result = groups.remove_user_from_group("u1", "grp-1")
        assert result is False
        assert "not in group" in capsys.readouterr().out

    def test_failure_fetching_group(self, capsys):
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", return_value=make_response(404)):
            result = groups.remove_user_from_group("u1", "grp-1")
        assert result is False
        assert "Failed" in capsys.readouterr().out

    def test_patch_failure(self, capsys):
        group_body = {"members": [{"value": "u1"}]}
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, group_body),
                 make_response(500),
             ]):
            result = groups.remove_user_from_group("u1", "grp-1")
        assert result is False

    def test_patch_sends_filtered_members(self):
        group_body = {"members": [{"value": "u1"}, {"value": "u2"}]}
        with patch.object(groups, "ensure_valid_config", return_value=CONFIG), \
             patch.object(groups, "make_request", side_effect=[
                 make_response(200, group_body),
                 make_response(200),
             ]) as mock_req:
            groups.remove_user_from_group("u1", "grp-1")
        members_sent = mock_req.call_args_list[1][1]["json_data"]["Operations"][0]["value"]
        assert {"value": "u1"} not in members_sent
        assert {"value": "u2"} in members_sent
