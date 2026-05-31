"""
Async OpenAI-compatible provider with key/model rotation.

Supports any provider that implements the OpenAI chat/completions API:
Groq, Cerebras, OpenRouter, Mistral, SambaNova, GitHub Models,
AI21, DeepSeek, NVIDIA NIM, and any custom endpoint.

Ported from translation_app.core.providers.openai_compatible_provider
and converted to async (httpx.AsyncClient).
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import httpx

from ai_providers.base import AIRequest, AIResult, BaseAIProvider, ProviderCandidate
from ai_providers.error_classifier import classify_error
from ai_providers.profiles import ProviderProfile, mask_key_suffix


class OpenAICompatibleProvider(BaseAIProvider):
    """Async provider wrapping any OpenAI-compatible chat/completions API."""

    def __init__(self, *, profile: ProviderProfile):
        normalized = profile.normalized()
        self.profile = normalized
        self.name = normalized.name
        self.display_name = normalized.display_name
        self.default_model = normalized.default_model or (
            normalized.model_pool[0] if normalized.model_pool else ""
        )
        self.enabled = normalized.enabled
        self.base_url = normalized.base_url.rstrip("/")
        self.api_key_pool = list(normalized.api_key_pool)
        self.model_pool = list(normalized.model_pool)
        self.timeout = normalized.timeout
        self._next_key_index = 0
        self._next_model_index = 0

    def is_available(self) -> bool:
        if not self.enabled or not self.base_url or not self.model_pool:
            return False
        return bool(self.api_key_pool)

    def iter_candidates(self) -> list[ProviderCandidate]:
        if not self.is_available():
            return []

        models = _rotate_list(self.model_pool, self._next_model_index)
        key_entries = list(enumerate(self.api_key_pool))
        key_entries = _rotate_list(key_entries, self._next_key_index)

        candidates: list[ProviderCandidate] = []
        for model in models:
            for key_index, key_value in key_entries:
                candidates.append(
                    ProviderCandidate(
                        provider_name=self.name,
                        model=model,
                        key_index=key_index,
                        key_id=mask_key_suffix(key_value),
                    )
                )
        return candidates

    async def call(
        self, request: AIRequest, candidate: ProviderCandidate | None = None
    ) -> AIResult:
        started = time.time()
        candidate = candidate or ProviderCandidate(
            provider_name=self.name,
            model=self.default_model,
            key_index=0 if self.api_key_pool else -1,
            key_id=mask_key_suffix(self.api_key_pool[0]) if self.api_key_pool else "",
        )

        messages = _build_messages(request)
        model_name = candidate.model or self.default_model
        # Cap max_tokens to a safe value (4096) for non-Gemini OpenAI-compatible providers to prevent HTTP 400
        safe_max_tokens = min(request.max_output_tokens or 4096, 4096)
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "max_tokens": safe_max_tokens,
            "temperature": request.temperature,
        }

        # JSON mode for providers that support it
        if request.response_schema:
            payload["response_format"] = {"type": "json_object"}

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "MatTheWebsite/1.0",
            "HTTP-Referer": "https://matthesinhhoa.vercel.app",
            "X-Title": "MatTheSinhHoaNguyCo",
        }
        api_key = self._resolve_api_key(candidate.key_index)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint = (
            f"{self.base_url}/chat/completions"
            if self.base_url.endswith("/v1")
            else f"{self.base_url}/v1/chat/completions"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)

            if response.is_success:
                data = response.json()
                text = _extract_message_text(data)
                return AIResult(
                    status="success",
                    text=text,
                    provider=self.name,
                    model=model_name,
                    key_id=candidate.key_id,
                    key_index=candidate.key_index,
                    latency_ms=round((time.time() - started) * 1000),
                )

            # Error response
            status_code = response.status_code
            raw_detail = response.text
            normalized_detail = _normalize_error_payload(raw_detail)
            detail = _sanitize_error_detail(normalized_detail or raw_detail, api_key)
            return AIResult(
                status="error",
                provider=self.name,
                model=model_name,
                key_id=candidate.key_id,
                key_index=candidate.key_index,
                error_type=classify_error(
                    None,
                    status_code=status_code,
                    response_body=normalized_detail or raw_detail,
                ),
                error_message=_format_http_error_message(status_code, detail),
                latency_ms=round((time.time() - started) * 1000),
            )
        except httpx.TimeoutException as exc:
            return AIResult(
                status="error",
                provider=self.name,
                model=model_name,
                key_id=candidate.key_id,
                key_index=candidate.key_index,
                error_type="timeout",
                error_message=f"Request timed out after {self.timeout}s: {exc}",
                latency_ms=round((time.time() - started) * 1000),
            )
        except Exception as exc:
            detail = _sanitize_error_detail(str(exc), api_key)
            return AIResult(
                status="error",
                provider=self.name,
                model=model_name,
                key_id=candidate.key_id,
                key_index=candidate.key_index,
                error_type=classify_error(exc),
                error_message=detail,
                latency_ms=round((time.time() - started) * 1000),
            )

    def mark_success(self, candidate: ProviderCandidate) -> None:
        if self.api_key_pool:
            self._next_key_index = (max(0, candidate.key_index) + 1) % len(
                self.api_key_pool
            )
        if self.model_pool and candidate.model in self.model_pool:
            self._next_model_index = self.model_pool.index(candidate.model)

    def mark_failure(self, candidate: ProviderCandidate, error_type: str) -> None:
        if self.api_key_pool and error_type in {
            "auth_failure",
            "quota_rate_limit",
            "transport_error",
            "timeout",
            "provider_5xx",
        }:
            self._next_key_index = (max(0, candidate.key_index) + 1) % len(
                self.api_key_pool
            )
        if self.model_pool and candidate.model in self.model_pool and error_type in {
            "model_error",
            "model_unavailable",
            "token_limit",
        }:
            self._next_model_index = (
                self.model_pool.index(candidate.model) + 1
            ) % len(self.model_pool)

    def _resolve_api_key(self, key_index: int) -> str:
        if key_index is None or key_index < 0 or key_index >= len(self.api_key_pool):
            return ""
        return self.api_key_pool[key_index]


def _build_messages(request: AIRequest) -> list[dict[str, str]]:
    """Build OpenAI-format message list from AIRequest."""
    messages: list[dict[str, str]] = []

    if request.system_instruction:
        messages.append({"role": "system", "content": request.system_instruction})

    if request.mode == "translation":
        user_content = _build_translation_prompt(request)
    elif request.mode == "chat":
        user_content = request.text
    else:
        user_content = request.text

    # If there's a response schema, append it as instruction
    if request.response_schema:
        schema_instruction = (
            "\n\nYou MUST respond with valid JSON matching this schema:\n"
            + json.dumps(request.response_schema, ensure_ascii=False, indent=2)
        )
        user_content += schema_instruction

    messages.append({"role": "user", "content": user_content})
    return messages


def _build_translation_prompt(request: AIRequest) -> str:
    """Build a translation prompt for OpenAI-compatible providers."""
    glossary_lines: list[str] = []
    for term in request.glossary_terms:
        source = str(term.get("source_term", "")).strip()
        target = str(term.get("target_term", "")).strip()
        if source and target:
            glossary_lines.append(f"{source} => {target}")

    glossary_part = ""
    if glossary_lines:
        glossary_part = (
            "\nUse this glossary strictly:\n" + "\n".join(glossary_lines) + "\n"
        )

    return (
        f"Translate the following text from {request.source_lang} to {request.target_lang}.\n"
        f"Provide ONLY the translation, without any explanations or notes."
        f"{glossary_part}"
        f"\nTEXT: {request.text}\n\nTRANSLATION:"
    )


def _extract_message_text(payload: dict) -> str:
    """Extract text from OpenAI chat completion response."""
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
        return "".join(parts).strip()
    return str(content).strip()


def _normalize_error_payload(raw_detail: str) -> str:
    """Extract meaningful error message from JSON error payloads."""
    detail = str(raw_detail or "")
    try:
        payload = json.loads(detail)
    except Exception:
        return detail

    error = payload.get("error")
    if isinstance(error, dict):
        values = [error.get("message"), error.get("type"), error.get("code")]
        return " ".join(str(value) for value in values if value)
    if isinstance(error, str):
        return error
    if payload.get("message"):
        return str(payload.get("message"))
    return detail


def _format_http_error_message(status_code: int | None, detail: str) -> str:
    if status_code is None and detail:
        return detail
    if status_code is None:
        return "HTTP error"
    if detail:
        return f"HTTP {status_code}: {detail}"
    return f"HTTP {status_code}"


def _sanitize_error_detail(detail: str, api_key: str = "") -> str:
    """Remove API keys from error messages."""
    sanitized = str(detail or "")
    if api_key:
        sanitized = sanitized.replace(api_key, "[REDACTED_API_KEY]")
    sanitized = re.sub(
        r"Authorization\s*:\s*Bearer\s+[^\s,;]+",
        "Authorization: [REDACTED_API_KEY]",
        sanitized,
        flags=re.IGNORECASE,
    )
    sanitized = re.sub(
        r"Bearer\s+[^\s,;]+",
        "Bearer [REDACTED_API_KEY]",
        sanitized,
        flags=re.IGNORECASE,
    )
    return sanitized[:500]


def _rotate_list(values: list, offset: int) -> list:
    """Rotate a list so element at offset comes first."""
    if not values:
        return []
    index = max(0, int(offset or 0)) % len(values)
    return list(values[index:]) + list(values[:index])
