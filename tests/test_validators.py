import pytest

from deywuro.exceptions import InvalidPhoneNumberError
from deywuro.validators import normalize_gh_number


def test_none_raises():
    with pytest.raises(InvalidPhoneNumberError):
        normalize_gh_number(None)


def test_empty_string_raises():
    with pytest.raises(InvalidPhoneNumberError):
        normalize_gh_number("")


def test_e164_plus_format():
    assert normalize_gh_number("+233266789453") == "233266789453"


def test_bare_233_format():
    assert normalize_gh_number("233266789453") == "233266789453"


def test_local_0_format():
    assert normalize_gh_number("0266789453") == "233266789453"


def test_non_gh_country_code_raises():
    with pytest.raises(InvalidPhoneNumberError):
        normalize_gh_number("+14155552671")


def test_too_short_raises():
    with pytest.raises(InvalidPhoneNumberError):
        normalize_gh_number("+23326678945")


def test_too_long_raises():
    with pytest.raises(InvalidPhoneNumberError):
        normalize_gh_number("+2332667894530")
