"""Ghanaian phone number normalization for the Deywuro API."""

from .exceptions import InvalidPhoneNumberError

GH_COUNTRY_CODE = "233"
GH_NATIONAL_DIGITS = 9
GH_TRUNK_PREFIX = "0"


def normalize_gh_number(phone: str) -> str:
    """
    Normalize a Ghanaian phone number to Deywuro's required format:
    233XXXXXXXXX (233 + 9 digits, no leading '+').

    Accepts +233XXXXXXXXX, 233XXXXXXXXX, or local 0XXXXXXXXX formats.

    Raises:
        InvalidPhoneNumberError: if the number isn't a valid Ghanaian MSISDN.
    """
    if not phone or not isinstance(phone, str):
        raise InvalidPhoneNumberError(f"Phone number is required, got: {phone!r}")

    digits = "".join(ch for ch in phone if ch.isdigit())

    # Local format e.g. 0266789453 -> strip leading 0, prefix 233
    if len(digits) == GH_NATIONAL_DIGITS + 1 and digits.startswith(GH_TRUNK_PREFIX):
        digits = GH_COUNTRY_CODE + digits[1:]

    if not digits.startswith(GH_COUNTRY_CODE):
        raise InvalidPhoneNumberError(
            f"Not a Ghanaian phone number (expected 233 country code): {phone}"
        )

    national_number = digits[len(GH_COUNTRY_CODE) :]
    if len(national_number) != GH_NATIONAL_DIGITS or not national_number.isdigit():
        raise InvalidPhoneNumberError(f"Malformed Ghanaian phone number: {phone}")

    return digits
