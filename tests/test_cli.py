from unittest.mock import patch

import scim_sim.cli as cli

CONFIG = {"SCIM_BASE_URL": "https://scim.example.com", "SCIM_AUTH_TOKEN": "token123"}


class TestMain:
    def _run(self, args):
        with patch("sys.argv", ["scim-sim"] + args):
            cli.main()

    def test_add_user(self):
        with patch.object(cli, "add_user") as mock:
            self._run(["add-user"])
        mock.assert_called_once()

    def test_remove_user(self):
        with patch.object(cli, "remove_user") as mock:
            self._run(["remove-user", "u1"])
        mock.assert_called_once_with("u1")

    def test_show(self):
        with patch.object(cli, "show_directory") as mock:
            self._run(["show"])
        mock.assert_called_once()

    def test_create_group(self):
        with patch.object(cli, "create_group") as mock:
            self._run(["create-group", "Engineering"])
        mock.assert_called_once_with("Engineering")

    def test_delete_group(self):
        with patch.object(cli, "delete_group") as mock:
            self._run(["delete-group", "grp-1"])
        mock.assert_called_once_with("grp-1")

    def test_add_to_group(self):
        with patch.object(cli, "add_user_to_group") as mock:
            self._run(["add-to-group", "u1", "grp-1"])
        mock.assert_called_once_with("u1", "grp-1")

    def test_remove_from_group(self):
        with patch.object(cli, "remove_user_from_group") as mock:
            self._run(["remove-from-group", "u1", "grp-1"])
        mock.assert_called_once_with("u1", "grp-1")

    def test_setup(self):
        with patch.object(cli, "setup_config") as mock:
            self._run(["setup"])
        mock.assert_called_once()

    def test_config(self, capsys):
        with patch.object(cli, "load_config", return_value=CONFIG):
            self._run(["config"])
        assert "SCIM_BASE_URL" in capsys.readouterr().out

    def test_no_command_prints_help(self, capsys):
        with patch("sys.argv", ["scim-sim"]):
            cli.main()
        captured = capsys.readouterr()
        assert "usage" in (captured.out + captured.err).lower()
