# Verify incoming webhook signatures

Every `POST` webhook from the billing service sends `X-Signature-Timestamp` and `X-Signature-256` headers signed with `HMAC-SHA256`. Verify both headers on your endpoint before queueing or processing any event, because unverified routes let callers forge billing state changes.

## Prerequisites

- Your endpoint signing secret (`WEBHOOK_SECRET`, prefixed `whsec_`) from `Settings > Webhooks`.
- Access to the raw, unparsed HTTP request body bytes in your route handler.
- Server clock synchronized via `NTP`.

## Verify each request

Warning: Read the raw HTTP request bytes before any JSON middleware runs. Re-serializing parsed JSON alters key order or whitespace and invalidates every `HMAC` digest.

Warning: Reject any request whose `X-Signature-Timestamp` lags or leads current `UTC` clock seconds by more than `300` before computing the digest.

1. Read the Unix epoch integer from the `X-Signature-Timestamp` header.
2. Return `401` if that timestamp drifts over `300` seconds from current server `UTC`.
3. Join the timestamp string, a literal period (`.`), and the raw `UTF-8` body bytes.
4. Compute the lowercase `HMAC-SHA256` hex digest of those combined bytes with `WEBHOOK_SECRET`.
5. Prepend `v1=` and match against `X-Signature-256` via `hmac.compare_digest` for constant-time comparison.

```python
import hashlib
import hmac
import time

TOLERANCE_SECONDS = 300


def verify_webhook(
    secret: str,
    timestamp_header: str,
    raw_body: bytes,
    signature_header: str,
) -> bool:
    try:
        sent_at = int(timestamp_header)
    except ValueError:
        return False

    if abs(int(time.time()) - sent_at) > TOLERANCE_SECONDS:
        return False

    signed_payload = timestamp_header.encode("utf-8") + b"." + raw_body
    expected = "v1=" + hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

## Test your endpoint locally

Sign a test payload with `openssl` and post it to your local listener with `curl`:

```bash
SECRET="whsec_test_secret"
TS="$(date +%s)"
BODY='{"id":"evt_01","type":"invoice.paid"}'
SIG="v1=$(printf '%s.%s' "$TS" "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')"

curl -i -X POST http://localhost:8080/webhooks \
  -H "Content-Type: application/json" \
  -H "X-Signature-Timestamp: $TS" \
  -H "X-Signature-256: $SIG" \
  --data-raw "$BODY"
```

Verify both outcomes before shipping to production:

- Sending a fresh timestamp and matching digest yields `200 OK`.
- Re-sending the request with `TS=$(( $(date +%s) - 600 ))` triggers `401 Unauthorized`.

For background on dual-secret rotation windows, see `docs/webhooks-architecture.md`.
