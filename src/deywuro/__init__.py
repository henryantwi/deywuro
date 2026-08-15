"""Unofficial Python client for the Deywuro (Npontu) SMS gateway."""

from .client import DeywuroClient, SendResult
from .exceptions import (
    DeywuroError,
    DeywuroRequestError,
    DeywuroServerError,
    InsufficientBalanceError,
    InvalidCredentialsError,
    InvalidPhoneNumberError,
    MissingFieldsError,
    NotRoutableError,
)
from .validators import normalize_gh_number

__version__ = "0.1.1"

__all__ = [
    "DeywuroClient",
    "DeywuroError",
    "DeywuroRequestError",
    "DeywuroServerError",
    "InsufficientBalanceError",
    "InvalidCredentialsError",
    "InvalidPhoneNumberError",
    "MissingFieldsError",
    "NotRoutableError",
    "SendResult",
    "__version__",
    "normalize_gh_number",
]


def __getattr__(name):
    if name == "AsyncDeywuroClient":
        from .async_client import AsyncDeywuroClient

        return AsyncDeywuroClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
