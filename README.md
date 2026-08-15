# deywuro

<img src="assets/deywuro-logo.png" alt="Deywuro logo" width="300">

*Deywuro's logo, shown for identification purposes only — this project is an
independent, unofficial client and is not published, endorsed, or affiliated
with Npontu Technologies.*

[![CI](https://github.com/henryantwi/deywuro/actions/workflows/ci.yml/badge.svg)](https://github.com/henryantwi/deywuro/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/deywuro.svg)](https://pypi.org/project/deywuro/)
[![Python versions](https://img.shields.io/pypi/pyversions/deywuro.svg)](https://pypi.org/project/deywuro/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Unofficial Python client for the [Deywuro](https://deywuro.com) (Npontu) SMS gateway.
Sends SMS to Ghanaian phone numbers via Deywuro's `/api/sms` endpoint.

Not affiliated with Npontu Technologies.

## Getting a Deywuro account and Sender ID

You need a Deywuro account, an API username/password, and an approved
Sender ID before you can send anything with this library. Here's how to get
all three, from scratch:

### 1. Create an account

1. Go to [deywuro.com/login](https://deywuro.com/login) and click
   **Create Account**.
2. Fill in the registration form:
   - **Register As** — `Client` (this is what you want, unless you're
     reselling Deywuro's service to your own customers, in which case pick
     `Reseller`)
   - **Name of Company/Individual** — your business name, or your own name
     if you're signing up individually
   - **Nature of Business** — pick the closest match from the dropdown
   - **Business Location**
   - **Preferred Username** — 6-30 characters, letters/numbers/underscore/
     hyphen. This becomes part of your API login, so pick something you're
     fine hard-coding into a `.env` file
   - **Contact Person Name / Email / Phone Number** — used for account
     verification and support
   - Optional: company phone number, mobile money number, business logo,
     business registration document, an **LOA (Letter of Authorization)**,
     and an ID for the contact person. You can skip all of these at signup —
     the LOA in particular is only needed later, for Sender ID approval (see
     below).
3. Submit the form. Npontu reviews new accounts manually, so expect a wait
   before you can log in.

### 2. Get your API credentials

Once your account is approved, log in at
[deywuro.com/login](https://deywuro.com/login). Your **API username** and
**password** are the credentials Npontu provisions for your account (the
username you chose at signup is usually what you'll use — confirm on your
dashboard, or ask support if you can't find them). These are the
`DEYWURO_USERNAME` / `DEYWURO_PASSWORD` values this library expects.

**Keep these secret** — treat them like any other API credential. Don't
commit them to source control; use environment variables or a `.env` file
that's git-ignored (see [Quickstart](#quickstart-sync) below).

### 3. Request a Sender ID

The `source` parameter (`DEYWURO_SOURCE` for this library) is your **Sender
ID** — the name recipients see as the SMS sender instead of a phone number
(e.g. `"MyApp"` instead of a shortcode). Requirements:

- Up to **11 characters**, alphanumeric.
- Must be **approved by Npontu** before messages sent with it will deliver
  reliably — an unapproved or unfamiliar sender ID risks being blocked by
  mobile network operators.
- To request one, submit an **LOA (Letter of Authorization)** — from your
  dashboard after logging in, or by emailing
  [support@npontu.com](mailto:support@npontu.com) if you don't see a
  self-service option. The LOA is essentially your business formally
  authorizing the use of that Sender ID.
- Approval isn't instant — ask support for current turnaround time when you
  submit.

While waiting for approval, some providers offer a shared/default test
Sender ID for development — ask support if one's available so you can test
integration before your own Sender ID clears.

### 4. Put it all together

```bash
# .env (never commit this file)
DEYWURO_USERNAME=your-approved-username
DEYWURO_PASSWORD=your-account-password
DEYWURO_SOURCE=YourSenderID
```

> **Note:** Deywuro's public materials don't fully document the post-login
> dashboard flow for credentials/Sender ID requests. If anything above
> doesn't match what you see after logging in, the fastest path is
> [support@npontu.com](mailto:support@npontu.com) — they provision accounts
> manually and can point you to the exact button/section.

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
