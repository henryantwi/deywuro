"""Exceptions raised by the Deywuro client."""

from __future__ import annotations


class DeywuroError(Exception):
    """Base exception for all Deywuro client errors."""

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


class InvalidCredentialsError(DeywuroError):
    """Raised when the API reports invalid username/password (code 401)."""


class MissingFieldsError(DeywuroError):
    """Raised when the API reports missing required fields (code 402)."""


class InsufficientBalanceError(DeywuroError):
    """Raised when the account has insufficient balance to send (code 403)."""


class NotRoutableError(DeywuroError):
    """Raised when the destination number isn't routable (code 404)."""


class DeywuroServerError(DeywuroError):
    """Raised for any other API-reported failure (code 500)."""


class DeywuroRequestError(DeywuroError):
    """Raised for network/transport-level failures (timeouts, connection
    errors, malformed responses) that never reach a Deywuro response code."""


class InvalidPhoneNumberError(DeywuroError):
    """Raised when a destination number isn't a valid Ghanaian MSISDN."""


_CODE_TO_EXCEPTION = {
    401: InvalidCredentialsError,
    402: MissingFieldsError,
    403: InsufficientBalanceError,
    404: NotRoutableError,
    500: DeywuroServerError,
}


def raise_for_code(code: int, message: str) -> None:
    """Raise the appropriate exception for a non-zero Deywuro response code.
    No-op if code is 0 (success)."""
    if code == 0:
        return
    exc_class = _CODE_TO_EXCEPTION.get(code, DeywuroServerError)
    raise exc_class(message, code=code)
