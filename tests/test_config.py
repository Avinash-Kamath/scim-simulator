import json
from unittest.mock import MagicMock, patch

import scim_sim.config as config

BASE_URL = "https://scim.example.com"
TOKEN = "token123"
CONFIG = {"SCIM_BASE_URL": BASE_URL, "SCIM_AUTH_TOKEN": TOKEN}
AUTH_HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def make_response(status_code, body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = body or {}
    resp.text = json.dumps(body or {})
    return resp


class TestIsValidUrl:
    def test_valid_http(self):
        assert config.is_valid_url("http://example.com") is True

    def test_valid_https(self):
        assert config.is_valid_url("https://scim.example.com/v2") is True

    def test_missing_scheme(self):
        assert config.is_valid_url("example.com") is False

    def test_missing_netloc(self):
        assert config.is_valid_url("https://") is False

    def test_empty_string(self):
        assert config.is_valid_url("") is False

    def test_ftp_scheme_rejected(self):
        assert config.is_valid_url("ftp://example.com") is False


class TestLoadConfig:
    def test_returns_dict_when_file_exists(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(CONFIG))
        with patch.object(config, "CONFIG_FILE", str(cfg_file)):
            result = config.load_config()
        assert result == CONFIG

    def test_returns_empty_dict_when_file_missing(self, tmp_path):
        with patch.object(config, "CONFIG_FILE", str(tmp_path / "missing.json")):
            result = config.load_config()
        assert result == {}


class TestSaveConfig:
    def test_writes_correct_json(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch.object(config, "CONFIG_FILE", str(cfg_file)):
            config.save_config(BASE_URL, TOKEN)
        saved = json.loads(cfg_file.read_text())
        assert saved["SCIM_BASE_URL"] == BASE_URL
        assert saved["SCIM_AUTH_TOKEN"] == TOKEN

    def test_prints_success(self, tmp_path, capsys):
        cfg_file = tmp_path / "config.json"
        with patch.object(config, "CONFIG_FILE", str(cfg_file)):
            config.save_config(BASE_URL, TOKEN)
        assert "saved successfully" in capsys.readouterr().out


class TestVerifyScimConfig:
    def test_returns_true_on_2xx(self):
        with patch.object(config, "make_request", return_value=make_response(200)) as mock_req:
            result = config.verify_scim_config(BASE_URL, TOKEN)
        assert result is True
        mock_req.assert_called_once_with("GET", f"{BASE_URL}/Users", headers=AUTH_HEADERS)

    def test_returns_true_on_201(self):
        with patch.object(config, "make_request", return_value=make_response(201)):
            assert config.verify_scim_config(BASE_URL, TOKEN) is True

    def test_returns_false_on_401(self, capsys):
        with patch.object(config, "make_request", return_value=make_response(401)):
            result = config.verify_scim_config(BASE_URL, TOKEN)
        assert result is False
        assert "invalid" in capsys.readouterr().out.lower()

    def test_returns_false_on_500(self):
        with patch.object(config, "make_request", return_value=make_response(500)):
            assert config.verify_scim_config(BASE_URL, TOKEN) is False


class TestEnsureValidConfig:
    def test_returns_config_when_valid(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(CONFIG))
        with patch.object(config, "CONFIG_FILE", str(cfg_file)), \
             patch.object(config, "verify_scim_config", return_value=True):
            result = config.ensure_valid_config()
        assert result == CONFIG

    def test_triggers_setup_when_config_missing(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        with patch.object(config, "CONFIG_FILE", str(cfg_file)), \
             patch.object(config, "setup_config") as mock_setup:
            def write_config():
                cfg_file.write_text(json.dumps(CONFIG))
            mock_setup.side_effect = write_config
            config.ensure_valid_config()
        mock_setup.assert_called_once()

    def test_triggers_setup_when_verify_fails(self, tmp_path):
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps(CONFIG))
        with patch.object(config, "CONFIG_FILE", str(cfg_file)), \
             patch.object(config, "verify_scim_config", return_value=False), \
             patch.object(config, "setup_config") as mock_setup:
            mock_setup.side_effect = lambda: None
            config.ensure_valid_config()
        mock_setup.assert_called_once()
