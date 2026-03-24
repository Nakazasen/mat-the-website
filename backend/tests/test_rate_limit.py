from fastapi import Request

from backend.rate_limit import InMemoryCooldownLimiter, get_client_ip


def _fake_request(headers: dict, client_host: str = "127.0.0.1") -> Request:
    scope = {
        "type": "http",
        "headers": [(k.lower().encode("utf-8"), v.encode("utf-8")) for k, v in headers.items()],
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_cooldown_limiter_blocks_within_window():
    limiter = InMemoryCooldownLimiter()
    allowed, retry_after = limiter.allow("k1", cooldown_seconds=3)
    assert allowed is True
    assert retry_after == 0

    allowed, retry_after = limiter.allow("k1", cooldown_seconds=3)
    assert allowed is False
    assert retry_after >= 1


def test_get_client_ip_prefers_forwarded_headers():
    req = _fake_request({"x-forwarded-for": "1.2.3.4, 5.6.7.8"})
    assert get_client_ip(req) == "1.2.3.4"

    req = _fake_request({"x-real-ip": "9.9.9.9"})
    assert get_client_ip(req) == "9.9.9.9"

    req = _fake_request({})
    assert get_client_ip(req) == "127.0.0.1"
