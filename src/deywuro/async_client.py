"""Asynchronous client for the Deywuro (Npontu) SMS gateway."""

from __future__ import annotations

import os

from .client import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, SendResult, _prepare_destination
from .exceptions import DeywuroRequestError, raise_for_code

try:
    import httpx
except ImportError as _exc:  # pragma: no cover
    httpx = None
    _httpx_import_error = _exc
else:
    _httpx_import_error = None


class AsyncDeywuroClient:
    """Async client for sending SMS via the Deywuro API.

    Requires the ``httpx`` extra: ``pip install deywuro[async]``.

    Example:
        client = AsyncDeywuroClient(username="user", password="pass", source="MyApp")
        await client.send("233266789453", "Hello there")
    """

    def __init__(
        self,
        username: str,
        password: str,
        source: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        client: httpx.AsyncClient | None = None,
    ):
        if httpx is None:
            raise ImportError(
                "AsyncDeywuroClient requires httpx. Install with: pip install deywuro[async]"
            ) from _httpx_import_error
        self.username = username
        self.password = password
        self.source = source
        self.base_url = base_url
        self.timeout = timeout
        self._client = client or httpx.AsyncClient()

    @classmethod
    def from_env(cls, **kwargs) -> AsyncDeywuroClient:
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

    async def send(
        self,
        destination: str | list[str],
        message: str,
        *,
        method: str = "GET",
        validate: bool = True,
    ) -> SendResult:
        """Async equivalent of DeywuroClient.send. See that method for details."""
        params = {
            "username": self.username,
            "password": self.password,
            "destination": _prepare_destination(destination, validate),
            "source": self.source,
            "message": message,
        }

        try:
            if method.upper() == "POST":
                response = await self._client.post(
                    self.base_url, data=params, timeout=self.timeout
                )
            else:
                response = await self._client.get(
                    self.base_url, params=params, timeout=self.timeout
                )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise DeywuroRequestError(f"Deywuro request failed: {exc}") from exc
        except ValueError as exc:
            raise DeywuroRequestError(
                f"Deywuro returned a non-JSON response: {exc}"
            ) from exc

        code = data.get("code")
        message_text = data.get("message", "")
        raise_for_code(code, message_text)

        return SendResult(code=code, message=message_text, raw=data)

    async def aclose(self) -> None:
        await self._client.aclose()
