"""
Async provider router with waterfall fallback, cooldown, and health tracking.

Ported from translation_app.core.provider_router.ProviderRouter
and converted to async for FastAPI.

Supports two routing modes:
- waterfall: Try providers in fixed order
- ai_pool_auto: Dynamic ranking by health status + quality score + latency
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Optional

from ai_providers.base import AIRequest, AIResult, BaseAIProvider
from ai_providers.error_classifier import COOLDOWN_ERROR_TYPES, FATAL_ERROR_TYPES, classify_error
from ai_providers.profiles import PROVIDER_QUALITY_SCORES


@dataclass
class ProviderState:
    """Runtime health state for a (provider, model, key) combination."""

    provider_name: str
    display_name: str = ""
    model: str = ""
    key_id: Optional[str] = None
    key_index: Optional[int] = None
    is_available: bool = True
    cooldown_until: float = 0.0
    consecutive_failures: int = 0
    last_error_type: str = ""
    last_latency_ms: int = 0
    success_count: int = 0
    failure_count: int = 0
    health_status: str = "healthy"  # healthy | degraded | cooldown | dead
    last_error_class: str = ""
    quality_score: float = 5.0
    latency_score: float = 0.0


class ProviderRouter:
    """Async runtime provider router with cooldown and health tracking."""

    def __init__(self, cooldown_seconds: int = 300, max_retries: int = 2):
        self.cooldown_seconds = max(1, int(cooldown_seconds))
        self.max_retries = max(0, int(max_retries))
        self._providers: dict[str, BaseAIProvider] = {}
        self._provider_states: dict[str, ProviderState] = {}

    def register_provider(self, provider: BaseAIProvider) -> None:
        """Register a provider for routing."""
        self._providers[provider.name] = provider
        self._ensure_state(
            provider.name,
            getattr(provider, "default_model", ""),
            display_name=getattr(provider, "display_name", provider.name),
        )

    async def route(
        self,
        request: AIRequest,
        policy: Optional[dict[str, Any]] = None,
    ) -> AIResult:
        """Route a request through available providers with fallback.

        Args:
            request: The AI request to fulfill.
            policy: Routing policy dict with optional keys:
                - mode: "waterfall" | "ai_pool_auto" (default: waterfall)
                - provider_order: List of provider names
                - allowed_providers: Set of allowed provider names

        Returns:
            AIResult with status "success" or "error".
        """
        policy = policy or {}
        ordered_names = self._resolve_order(
            policy.get("provider_order"),
            policy.get("allowed_providers"),
            policy,
        )
        # Set a generous limit for total attempts across all providers to ensure fallback works
        max_attempts = max(15, (self.max_retries + 1) * len(ordered_names))
        attempts: list[dict[str, Any]] = []
        total_attempts = 0

        if max_attempts <= 0:
            return AIResult(
                status="error",
                error_type="no_provider_available",
                error_message="No eligible AI providers are available.",
                attempts=attempts,
            )

        for provider_name in ordered_names:
            provider = self._providers.get(provider_name)
            if provider is None:
                continue

            if not provider.is_available():
                state = self._ensure_state(
                    provider.name,
                    getattr(provider, "default_model", ""),
                    display_name=getattr(provider, "display_name", provider.name),
                )
                state.is_available = False
                state.last_error_type = "unavailable"
                attempts.append(
                    {
                        "provider": provider.name,
                        "display_name": getattr(
                            provider, "display_name", provider.name
                        ),
                        "model": getattr(provider, "default_model", ""),
                        "status": "skipped",
                        "reason": "unavailable",
                    }
                )
                continue

            candidates = provider.iter_candidates()
            if not candidates:
                attempts.append(
                    {
                        "provider": provider.name,
                        "display_name": getattr(
                            provider, "display_name", provider.name
                        ),
                        "model": getattr(provider, "default_model", ""),
                        "status": "skipped",
                        "reason": "no_candidates",
                    }
                )
                continue

            # Try at most 5 candidates for this provider before falling back to the next provider
            provider_attempts = 0
            for candidate in candidates:
                if provider_attempts >= 5:
                    break
                if total_attempts >= max_attempts:
                    break
                provider_attempts += 1

                state = self._ensure_state(
                    provider.name,
                    candidate.model or getattr(provider, "default_model", ""),
                    key_index=candidate.key_index,
                    key_id=candidate.key_id,
                    display_name=getattr(provider, "display_name", provider.name),
                )
                if self._is_on_cooldown(state):
                    attempts.append(
                        {
                            "provider": provider.name,
                            "display_name": getattr(
                                provider, "display_name", provider.name
                            ),
                            "model": candidate.model,
                            "key_index": candidate.key_index,
                            "key_id": candidate.key_id,
                            "status": "skipped",
                            "reason": "cooldown",
                        }
                    )
                    continue

                total_attempts += 1
                result = await provider.call(request, candidate)
                result.provider = result.provider or provider.name
                result.model = result.model or candidate.model or getattr(
                    provider, "default_model", ""
                )
                result.key_index = candidate.key_index
                result.key_id = candidate.key_id

                if result.status == "success":
                    self.mark_success(
                        result.provider,
                        result.model,
                        result.latency_ms,
                        key_index=candidate.key_index,
                        key_id=candidate.key_id,
                        display_name=getattr(
                            provider, "display_name", provider.name
                        ),
                    )
                    provider.mark_success(candidate)
                    attempts.append(
                        {
                            "provider": result.provider,
                            "display_name": getattr(
                                provider, "display_name", provider.name
                            ),
                            "model": result.model,
                            "key_index": candidate.key_index,
                            "key_id": candidate.key_id,
                            "status": "success",
                            "latency_ms": result.latency_ms,
                        }
                    )
                    result.attempts = attempts
                    return result

                # Failed — record and continue
                error_detail = (
                    result.error_type or result.error_message or "provider_error"
                )
                self.mark_failure(
                    result.provider or provider.name,
                    result.model or candidate.model,
                    error_detail,
                    result.latency_ms,
                    key_index=candidate.key_index,
                    key_id=candidate.key_id,
                    display_name=getattr(provider, "display_name", provider.name),
                )
                provider.mark_failure(candidate, result.error_type or "error")
                attempts.append(
                    {
                        "provider": result.provider or provider.name,
                        "display_name": getattr(
                            provider, "display_name", provider.name
                        ),
                        "model": result.model or candidate.model,
                        "key_index": candidate.key_index,
                        "key_id": candidate.key_id,
                        "status": "failed",
                        "reason": result.error_type or "error",
                        "message": result.error_message,
                        "latency_ms": result.latency_ms,
                    }
                )

            if total_attempts >= max_attempts:
                break

        # All attempts exhausted
        final_attempt = attempts[-1] if attempts else {}
        error_message = str(
            final_attempt.get("message", "No AI provider succeeded.")
        )
        return AIResult(
            status="error",
            provider=str(final_attempt.get("provider", "")),
            model=str(final_attempt.get("model", "")),
            error_type=str(
                final_attempt.get("reason", "no_provider_available")
            ),
            error_message=error_message,
            latency_ms=int(final_attempt.get("latency_ms", 0) or 0),
            attempts=attempts,
        )

    def mark_success(
        self,
        provider: str,
        model: str,
        latency_ms: int = 0,
        *,
        key_index: int | None = None,
        key_id: str | None = None,
        display_name: str = "",
    ) -> None:
        state = self._ensure_state(
            provider, model, key_index=key_index, key_id=key_id, display_name=display_name
        )
        state.model = model or state.model
        state.is_available = True
        state.cooldown_until = 0.0
        state.consecutive_failures = 0
        state.last_error_type = ""
        state.last_latency_ms = max(0, int(latency_ms or 0))
        state.success_count += 1
        state.health_status = "healthy"
        if latency_ms > 0:
            if state.latency_score <= 0:
                state.latency_score = float(latency_ms)
            else:
                state.latency_score = 0.8 * state.latency_score + 0.2 * float(
                    latency_ms
                )

    def mark_failure(
        self,
        provider: str,
        model: str,
        error: Any,
        latency_ms: int = 0,
        *,
        key_index: int | None = None,
        key_id: str | None = None,
        display_name: str = "",
    ) -> None:
        state = self._ensure_state(
            provider, model, key_index=key_index, key_id=key_id, display_name=display_name
        )
        error_type = classify_error(error)
        state.model = model or state.model
        state.is_available = error_type not in FATAL_ERROR_TYPES
        state.consecutive_failures += 1
        state.last_error_type = error_type
        state.last_latency_ms = max(0, int(latency_ms or 0))
        state.failure_count += 1
        state.last_error_class = error_type

        if error_type in FATAL_ERROR_TYPES:
            state.health_status = "dead"
        elif error_type in ("quota_rate_limit", "token_limit"):
            state.health_status = "cooldown"
        elif error_type in ("timeout", "provider_5xx"):
            state.health_status = "degraded"

        if latency_ms > 0:
            if state.latency_score <= 0:
                state.latency_score = float(latency_ms)
            else:
                state.latency_score = 0.8 * state.latency_score + 0.2 * float(
                    latency_ms
                )

        if error_type in COOLDOWN_ERROR_TYPES:
            state.cooldown_until = time.time() + self.cooldown_seconds

    def get_health_snapshot(self) -> list[dict[str, Any]]:
        """Return current health state for all tracked providers."""
        snapshots: list[dict[str, Any]] = []
        now = time.time()
        for state in self._provider_states.values():
            payload = asdict(state)
            payload["is_available"] = state.is_available and not self._is_on_cooldown(
                state, now
            )
            payload["cooldown_until"] = (
                round(state.cooldown_until, 3) if state.cooldown_until else 0.0
            )
            snapshots.append(payload)
        snapshots.sort(key=lambda item: (item["provider_name"], item["model"]))
        return snapshots

    def reset_cooldowns(self) -> None:
        """Clear all cooldowns and restore availability."""
        for state in self._provider_states.values():
            state.cooldown_until = 0.0
            state.is_available = True
            state.consecutive_failures = 0
            state.last_error_type = ""
            state.health_status = "healthy"

    def _resolve_order(
        self,
        preferred: Optional[Iterable[str]],
        allowed: Optional[Iterable[str]],
        policy: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        policy = policy or {}
        policy_mode = policy.get("mode", "")
        allowed_set = {
            item
            for item in (allowed or self._providers.keys())
            if item in self._providers
        }

        # Dynamic ranking mode
        if policy_mode == "ai_pool_auto":

            def get_provider_rank(name: str) -> tuple:
                provider_states = [
                    s
                    for s in self._provider_states.values()
                    if s.provider_name == name
                ]
                if not provider_states:
                    provider_states = [self._ensure_state(name)]

                is_available = any(s.is_available for s in provider_states)
                is_cooldown = all(
                    self._is_on_cooldown(s) for s in provider_states
                )
                health_set = {s.health_status for s in provider_states}

                if "healthy" in health_set:
                    health_status = "healthy"
                elif "degraded" in health_set:
                    health_status = "degraded"
                elif "cooldown" in health_set:
                    health_status = "cooldown"
                else:
                    health_status = "dead"

                if not is_available:
                    status_rank = 4
                elif is_cooldown:
                    status_rank = 3
                elif health_status == "degraded":
                    status_rank = 1
                else:
                    status_rank = 0

                quality = max(
                    (
                        getattr(s, "quality_score", 5.0)
                        for s in provider_states
                    ),
                    default=5.0,
                )
                latencies = [
                    getattr(s, "latency_score", 0.0)
                    for s in provider_states
                    if getattr(s, "latency_score", 0.0) > 0
                ]
                latency = sum(latencies) / len(latencies) if latencies else 500.0

                return (status_rank, -quality, latency)

            return sorted(allowed_set, key=get_provider_rank)

        # Default waterfall mode
        order = [
            name
            for name in (preferred or self._providers.keys())
            if name in allowed_set
        ]
        for name in allowed_set:
            if name not in order:
                order.append(name)
        return order

    def _ensure_state(
        self,
        provider: str,
        model: str = "",
        *,
        key_index: int | None = None,
        key_id: str | None = None,
        display_name: str = "",
    ) -> ProviderState:
        key = f"{provider}::{model}::{key_index if key_index is not None else -1}"
        if key not in self._provider_states:
            self._provider_states[key] = ProviderState(
                provider_name=provider,
                display_name=display_name or provider,
                model=model,
                key_id=key_id or None,
                key_index=key_index,
                quality_score=PROVIDER_QUALITY_SCORES.get(provider, 5.0),
            )
        return self._provider_states[key]

    def _is_on_cooldown(
        self, state: ProviderState, now: Optional[float] = None
    ) -> bool:
        if state.cooldown_until <= 0:
            return False
        current = now if now is not None else time.time()
        return state.cooldown_until > current
