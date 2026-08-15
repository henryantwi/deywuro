from unittest.mock import MagicMock, patch

from deywuro.cli import main
from deywuro.client import SendResult
from deywuro.exceptions import InsufficientBalanceError


@patch("deywuro.cli.DeywuroClient")
def test_send_success(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_client.send.return_value = SendResult(code=0, message="sent", raw={})
    mock_client_class.return_value = mock_client

    exit_code = main(
        [
            "send",
            "--to",
            "233266789453",
            "--message",
            "hi",
            "--username",
            "u",
            "--password",
            "p",
            "--source",
            "src",
        ]
    )

    assert exit_code == 0
    out = capsys.readouterr().out
    assert '"code": 0' in out


@patch("deywuro.cli.DeywuroClient")
def test_send_failure_exits_nonzero(mock_client_class, capsys):
    mock_client = MagicMock()
    mock_client.send.side_effect = InsufficientBalanceError("no balance", code=403)
    mock_client_class.return_value = mock_client

    exit_code = main(
        [
            "send",
            "--to",
            "233266789453",
            "--message",
            "hi",
            "--username",
            "u",
            "--password",
            "p",
            "--source",
            "src",
        ]
    )

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "no balance" in err


def test_missing_credentials_exits_nonzero(monkeypatch, capsys):
    monkeypatch.delenv("DEYWURO_USERNAME", raising=False)
    monkeypatch.delenv("DEYWURO_PASSWORD", raising=False)
    monkeypatch.delenv("DEYWURO_SOURCE", raising=False)

    exit_code = main(["send", "--to", "233266789453", "--message", "hi"])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "Missing required credentials" in err
