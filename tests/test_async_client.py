import httpx
import pytest
import respx

from deywuro.async_client import AsyncDeywuroClient
from deywuro.exceptions import (
    DeywuroRequestError,
    InsufficientBalanceError,
    InvalidPhoneNumberError,
)

BASE_URL = "https://deywuro.com/api/sms"


@pytest.mark.asyncio
@respx.mock
async def test_success():
    respx.get(BASE_URL).mock(
        return_value=httpx.Response(200, json={"code": 0, "message": "sent"})
    )
    client = AsyncDeywuroClient(username="u", password="p", source="src")

    result = await client.send("233266789453", "hello")

    assert result.code == 0
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_error_code_raises():
    respx.get(BASE_URL).mock(
        return_value=httpx.Response(200, json={"code": 403, "message": "no balance"})
    )
    client = AsyncDeywuroClient(username="u", password="p", source="src")

    with pytest.raises(InsufficientBalanceError):
        await client.send("233266789453", "hello")
    await client.aclose()


@pytest.mark.asyncio
async def test_invalid_number_raises():
    client = AsyncDeywuroClient(username="u", password="p", source="src")

    with pytest.raises(InvalidPhoneNumberError):
        await client.send("+14155552671", "hello")
    await client.aclose()


@pytest.mark.asyncio
@respx.mock
async def test_network_error_raises_request_error():
    respx.get(BASE_URL).mock(side_effect=httpx.ConnectError("down"))
    client = AsyncDeywuroClient(username="u", password="p", source="src")

    with pytest.raises(DeywuroRequestError):
        await client.send("233266789453", "hello")
    await client.aclose()
