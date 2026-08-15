# deywuro

Unofficial Python client for the [Deywuro](https://deywuro.com) (Npontu) SMS gateway.
Sends SMS to Ghanaian phone numbers via Deywuro's `/api/sms` endpoint.

Not affiliated with Npontu Technologies.

## Install

```bash
pip install deywuro

# For the async client:
pip install deywuro[async]
```

## Quickstart (sync)

```python
from deywuro import DeywuroClient

client = DeywuroClient(
    username="your-username", password="your-password", source="MyApp"
)
result = client.send("233266789453", "Hello there")
print(result.code, result.message)
```

Or build from environment variables (`DEYWURO_USERNAME`, `DEYWURO_PASSWORD`, `DEYWURO_SOURCE`):

```python
client = DeywuroClient.from_env()
client.send(["233266789453", "0201234567"], "Hello there")
```

## Quickstart (async)

```python
import asyncio
from deywuro import AsyncDeywuroClient


async def main():
    client = AsyncDeywuroClient.from_env()
    result = await client.send("233266789453", "Hello there")
    print(result.code, result.message)
    await client.aclose()


asyncio.run(main())
```

## CLI

```bash
export DEYWURO_USERNAME=your-username
export DEYWURO_PASSWORD=your-password
export DEYWURO_SOURCE=MyApp

deywuro send --to 233266789453 --message "Hello there"
```

## Error handling

All API failures raise a typed exception (subclass of `DeywuroError`):

| Code | Exception |
|---|---|
| 401 | `InvalidCredentialsError` |
| 402 | `MissingFieldsError` |
| 403 | `InsufficientBalanceError` |
| 404 | `NotRoutableError` |
| 500 | `DeywuroServerError` |
| n/a | `DeywuroRequestError` (network/transport failure) |
| n/a | `InvalidPhoneNumberError` (invalid destination number) |

```python
from deywuro import DeywuroClient, DeywuroError

client = DeywuroClient.from_env()
try:
    client.send("233266789453", "Hello there")
except DeywuroError as e:
    print(f"Send failed ({e.code}): {e.message}")
```

## Phone number handling

Destinations are validated and normalized to Deywuro's required `233XXXXXXXXX`
format by default. Accepted input formats: `+233266789453`, `233266789453`,
`0266789453`. Pass `validate=False` to `send()` to skip this.

## Scope

Only the send-SMS endpoint is implemented — it's the only endpoint documented
in Deywuro's public API reference. No balance-check or delivery-status API is
currently published by Npontu.

## License

MIT
