"""
Error classification for AI provider responses.

Maps raw errors (HTTP status codes, error messages) to standardized categories
used by the router for cooldown, fallback, and health tracking decisions.

Ported from translation_app.core.provider_router.classify_error.
"""

from __future__ import annotations

from typing import Any


AUTH_HINTS = (
    "401",
    "403",
    "unauthorized",
    "authentication",
    "auth failure",
    "invalid api key",
    "incorrect api key",
    "permission denied",
    "forbidden",
    "api key",
    "invalid key",
)
QUOTA_HINTS = (
    "429",
    "quota",
    "rate limit",
    "rate_limit",
    "resource exhausted",
    "too many requests",
)
TIMEOUT_HINTS = ("timeout", "timed out")
TRANSPORT_HINTS = (
    "connection failed",
    "connection aborted",
    "connection refused",
    "connection reset",
    "connection error",
    "actively refused",
    "remote end closed connection",
    "temporary failure in name resolution",
    "name or service not known",
    "no address associated with hostname",
    "network is unreachable",
    "failed to establish a new connection",
    "max retries exceeded",
)
MODEL_UNAVAILABLE_HINTS = ("404", "410", "not found", "model unavailable")
MODEL_ERROR_HINTS = (
    "invalid model",
    "model not found",
    "unknown model",
    "unsupported model",
)
TOKEN_LIMIT_HINTS = ("token limit", "token_limit", "prompt token", "context length")
PROVIDER_5XX_HINTS = (
    "500",
    "502",
    "503",
    "504",
    "server error",
    "bad gateway",
    "service unavailable",
    "gateway timeout",
)

# All error types the system recognizes
COOLDOWN_ERROR_TYPES = frozenset(
    {
        "auth_failure",
        "quota_rate_limit",
        "token_limit",
        "timeout",
        "transport_error",
        "model_unavailable",
        "model_error",
        "provider_5xx",
        "unknown_transport_error",
    }
)
FATAL_ERROR_TYPES = frozenset({"auth_failure"})


def classify_error(
    error: Any,
    status_code: int | None = None,
    response_body: Any = None,
) -> str:
    """Classify an error into a standardized category.

    Returns one of:
      auth_failure, quota_rate_limit, token_limit, timeout,
      transport_error, model_unavailable, model_error,
      provider_5xx, unknown_transport_error
    """
    # Fast path: HTTP status code checks
    if status_code in (401, 403):
        return "auth_failure"
    if status_code == 429:
        return "quota_rate_limit"
    if status_code == 400:
        detail_400 = _build_error_detail(error, response_body)
        if any(token in detail_400 for token in MODEL_ERROR_HINTS):
            return "model_error"
    if status_code in (404, 410):
        detail_404 = _build_error_detail(error, response_body)
        if any(
            token in detail_404
            for token in MODEL_ERROR_HINTS + MODEL_UNAVAILABLE_HINTS
        ):
            return "model_unavailable"
    if status_code is not None and 500 <= status_code <= 599:
        return "provider_5xx"

    # Slow path: string matching on error detail
    detail = _build_error_detail(error, response_body)

    if any(token in detail for token in AUTH_HINTS):
        return "auth_failure"
    if any(token in detail for token in QUOTA_HINTS):
        return "quota_rate_limit"
    if "400" in detail and any(token in detail for token in MODEL_ERROR_HINTS):
        return "model_error"
    if any(token in detail for token in TOKEN_LIMIT_HINTS):
        return "token_limit"
    if any(token in detail for token in TIMEOUT_HINTS):
        return "timeout"
    if any(token in detail for token in TRANSPORT_HINTS):
        return "transport_error"
    if any(token in detail for token in MODEL_ERROR_HINTS):
        return "model_error"
    if any(token in detail for token in MODEL_UNAVAILABLE_HINTS):
        return "model_unavailable"
    if any(token in detail for token in PROVIDER_5XX_HINTS):
        return "provider_5xx"
    return "unknown_transport_error"


def _build_error_detail(error: Any, response_body: Any = None) -> str:
    """Build a lowercase search string from error and response body."""
    parts: list[str] = []

    if response_body:
        if isinstance(response_body, dict):
            parts.append(" ".join(str(value) for value in response_body.values()))
        else:
            parts.append(str(response_body))

    if isinstance(error, str):
        parts.append(error)
    elif isinstance(error, dict):
        parts.append(" ".join(str(value) for value in error.values()))
    elif error is not None:
        parts.append(type(error).__name__)
        parts.append(str(error))

    return " ".join(part for part in parts if part).lower()
