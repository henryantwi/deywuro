import json
from unittest.mock import MagicMock

import pytest
import requests

from deywuro.client import DeywuroClient, SendResult
from deywuro.exceptions import (
    DeywuroRequestError,
    DeywuroServerError,
    InsufficientBalanceError,
    InvalidCredentialsError,
    InvalidPhoneNumberError,
    MissingFieldsError,
    NotRoutableError,
)


def _mock_response(payload, status_ok=True):
    resp = MagicMock()
    resp.json.return_value = payload
    if status_ok:
        resp.raise_for_status.return_value = None
    else:
        resp.raise_for_status.side_effect = requests.exceptions.HTTPError("bad status")
    return resp


class TestSend:
    def test_success(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.get.return_value = _mock_response(
            {"code": 0, "message": "1 sms successfully sent!"}
        )

        result = client.send("233266789453", "hello")

        assert isinstance(result, SendResult)
        assert result.code == 0
        call_kwargs = client.session.get.call_args
        assert call_kwargs[1]["params"]["destination"] == "233266789453"

    def test_multiple_destinations_list(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.get.return_value = _mock_response({"code": 0, "message": "ok"})

        client.send(["233266789453", "0201234567"], "hello")

        params = client.session.get.call_args[1]["params"]
        assert params["destination"] == "233266789453,233201234567"

    def test_validate_false_bypasses_normalization(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.get.return_value = _mock_response({"code": 0, "message": "ok"})

        client.send("not-a-real-number", "hello", validate=False)

        params = client.session.get.call_args[1]["params"]
        assert params["destination"] == "not-a-real-number"

    def test_invalid_number_raises(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()

        with pytest.raises(InvalidPhoneNumberError):
            client.send("+14155552671", "hello")
        client.session.get.assert_not_called()

    @pytest.mark.parametrize(
        "code,exc_class",
        [
            (401, InvalidCredentialsError),
            (402, MissingFieldsError),
            (403, InsufficientBalanceError),
            (404, NotRoutableError),
            (500, DeywuroServerError),
        ],
    )
    def test_error_codes_raise_typed_exceptions(self, code, exc_class):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.get.return_value = _mock_response(
            {"code": code, "message": "failure"}
        )

        with pytest.raises(exc_class):
            client.send("233266789453", "hello")

    def test_post_method(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.post.return_value = _mock_response({"code": 0, "message": "ok"})

        client.send("233266789453", "hello", method="POST")

        client.session.post.assert_called_once()
        client.session.get.assert_not_called()

    def test_network_error_raises_request_error(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        client.session.get.side_effect = requests.exceptions.ConnectionError("down")

        with pytest.raises(DeywuroRequestError):
            client.send("233266789453", "hello")

    def test_malformed_json_raises_request_error(self):
        client = DeywuroClient(username="u", password="p", source="src")
        client.session = MagicMock()
        resp = MagicMock()
        resp.raise_for_status.return_value = None
        resp.json.side_effect = json.JSONDecodeError("bad", "doc", 0)
        client.session.get.return_value = resp

        with pytest.raises(DeywuroRequestError):
            client.send("233266789453", "hello")


class TestFromEnv:
    def test_builds_from_env_vars(self, monkeypatch):
        monkeypatch.setenv("DEYWURO_USERNAME", "u")
        monkeypatch.setenv("DEYWURO_PASSWORD", "p")
        monkeypatch.setenv("DEYWURO_SOURCE", "src")

        client = DeywuroClient.from_env()

        assert client.username == "u"
        assert client.password == "p"
        assert client.source == "src"

    def test_missing_env_var_raises(self, monkeypatch):
        monkeypatch.delenv("DEYWURO_USERNAME", raising=False)
        monkeypatch.delenv("DEYWURO_PASSWORD", raising=False)
        monkeypatch.delenv("DEYWURO_SOURCE", raising=False)

        with pytest.raises(DeywuroRequestError):
            DeywuroClient.from_env()
