from unittest.mock import MagicMock, patch

import scim_sim.client as client


def make_response(status_code):
    resp = MagicMock()
    resp.status_code = status_code
    return resp


class TestMakeRequest:
    def test_delegates_to_requests(self):
        mock_resp = make_response(200)
        with patch("requests.request", return_value=mock_resp) as mock_req:
            result = client.make_request("GET", "https://example.com",
                                         headers={"A": "B"}, json_data={"x": 1})
        mock_req.assert_called_once_with("GET", "https://example.com",
                                          headers={"A": "B"}, json={"x": 1})
        assert result is mock_resp

    def test_returns_response(self):
        mock_resp = make_response(204)
        with patch("requests.request", return_value=mock_resp):
            result = client.make_request("DELETE", "https://example.com")
        assert result.status_code == 204
