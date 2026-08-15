"""Synchronous client for the Deywuro (Npontu) SMS gateway."""

from __future__ import annotations

import os
from dataclasses import dataclass

import requests

from .exceptions import DeywuroRequestError, raise_for_code
from .validators import normalize_gh_number

DEFAULT_BASE_URL = "https://deywuro.com/api/sms"
DEFAULT_TIMEOUT = 10


@dataclass
class SendResult:
    """Result of a successful SMS send."""

    code: int
    message: str
    raw: dict


def _prepare_destination(destination: str | list[str], validate: bool) -> str:
    if isinstance(destination, str):
        numbers = [n.strip() for n in destination.split(",") if n.strip()]
    else:
        numbers = list(destination)

    if validate:
        numbers = [normalize_gh_number(n) for n in numbers]

    return ",".join(numbers)


class DeywuroClient:
    """Client for sending SMS via the Deywuro API.

    Example:
        client = DeywuroClient(username="user", password="pass", source="MyApp")
        client.send("233266789453", "Hello there")
    """

    def __init__(
        self,
        username: str,
        password: str,
        source: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ):
        self.username = username
        self.password = password
        self.source = source
        self.base_url = base_url
        self.timeout = timeout
        self.session = session or requests.Session()

    @classmethod
    def from_env(cls, **kwargs) -> DeywuroClient:
        """Build a client from DEYWURO_USERNAME, DEYWURO_PASSWORD, DEYWURO_SOURCE
        environment variables."""
        try:
            username = os.environ["DEYWURO_USERNAME"]
            password = os.environ["DEYWURO_PASSWORD"]
            source = os.environ["DEYWURO_SOURCE"]
        except KeyError as exc:
            raise DeywuroRequestError(
                f"Missing required environment variable: {exc.args[0]}"
            ) from exc
        return cls(username=username, password=password, source=source, **kwargs)

    def send(
        self,
        destination: str | list[str],
        message: str,
        *,
        method: str = "GET",
        validate: bool = True,
    ) -> SendResult:
        """Send an SMS to one or more destinations.

        Args:
            destination: A single MSISDN, a comma-separated string of MSISDNs,
                or a list of MSISDNs.
            message: The SMS body.
            method: "GET" or "POST" (Deywuro accepts both).
            validate: Normalize/validate each destination as a Ghanaian
                number before sending. Set False to bypass (e.g. non-GH
                numbers if Deywuro ever supports them).

        Returns:
            SendResult on success.

        Raises:
            InvalidPhoneNumberError: if validate=True and a number is invalid.
            InvalidCredentialsError, MissingFieldsError, InsufficientBalanceError,
            NotRoutableError, DeywuroServerError: on API-reported failure.
            DeywuroRequestError: on network/transport failure.
        """
        params = {
            "username": self.username,
            "password": self.password,
            "destination": _prepare_destination(destination, validate),
            "source": self.source,
            "message": message,
        }

        try:
            if method.upper() == "POST":
                response = self.session.post(
                    self.base_url, data=params, timeout=self.timeout
                )
            else:
                response = self.session.get(
                    self.base_url, params=params, timeout=self.timeout
                )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            raise DeywuroRequestError(f"Deywuro request failed: {exc}") from exc
        except ValueError as exc:
            raise DeywuroRequestError(
                f"Deywuro returned a non-JSON response: {exc}"
            ) from exc

        code = data.get("code")
        message_text = data.get("message", "")
        raise_for_code(code, message_text)

        return SendResult(code=code, message=message_text, raw=data)
