"""
Base provider contract and data classes for the multi-provider AI system.

Adapted from translation_app patterns for async FastAPI usage.
Supports translation, chat, and completion modes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ProviderCandidate:
    """Represents a specific (provider, model, key) combination to try."""

    provider_name: str
    model: str = ""
    key_index: int = -1
    key_id: str = ""


@dataclass
class AIRequest:
    """Unified request for translation, chat, or completion."""

    text: str
    mode: str = "chat"  # "translation" | "chat" | "completion"
    source_lang: str = ""
    target_lang: str = ""
    system_instruction: str = ""
    context: str = ""
    response_schema: Optional[dict[str, Any]] = None
    glossary_terms: list[dict[str, Any]] = field(default_factory=list)
    max_output_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    strategy: str = "waterfall"
    job_id: Optional[str] = None


@dataclass
class AIResult:
    """Unified result from any provider."""

    status: str  # "success" | "error"
    text: str = ""
    provider: str = ""
    model: str = ""
    key_id: str = ""
    key_index: int = -1
    error_type: str = ""
    error_message: str = ""
    retry_after_seconds: float = 0.0
    latency_ms: int = 0
    from_cache: bool = False
    attempts: list[dict[str, Any]] = field(default_factory=list)


class BaseAIProvider(ABC):
    """Abstract base for all AI providers.

    Each provider must implement:
    - is_available(): Can this provider handle requests right now?
    - call(): Execute a single AI request with a specific candidate.
    - iter_candidates(): Yield all (model, key) combos to try.
    """

    name: str = "base"
    display_name: str = "Base"
    default_model: str = ""

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def call(
        self, request: AIRequest, candidate: ProviderCandidate | None = None
    ) -> AIResult:
        raise NotImplementedError

    def iter_candidates(self) -> list[ProviderCandidate]:
        return [ProviderCandidate(provider_name=self.name, model=self.default_model)]

    def mark_success(self, candidate: ProviderCandidate) -> None:
        return None

    def mark_failure(self, candidate: ProviderCandidate, error_type: str) -> None:
        return None
