"""
Multi-provider AI system for mat-the-website.

Provides async AI routing across multiple free-tier providers
with automatic failover, health tracking, and key rotation.

No Gemini or Google Translate dependency.
"""

from ai_providers.base import (
    AIRequest,
    AIResult,
    BaseAIProvider,
    ProviderCandidate,
)
from ai_providers.error_classifier import classify_error
from ai_providers.health import ProviderHealthChecker, ProviderHealthResult
from ai_providers.openai_compatible import OpenAICompatibleProvider
from ai_providers.profiles import (
    ProviderProfile,
    build_provider_profiles,
    get_default_provider_profiles,
    mask_key_suffix,
    PROVIDER_QUALITY_SCORES,
)
from ai_providers.router import ProviderRouter, ProviderState

__all__ = [
    "AIRequest",
    "AIResult",
    "BaseAIProvider",
    "OpenAICompatibleProvider",
    "ProviderCandidate",
    "ProviderHealthChecker",
    "ProviderHealthResult",
    "ProviderProfile",
    "ProviderRouter",
    "ProviderState",
    "build_provider_profiles",
    "classify_error",
    "get_default_provider_profiles",
    "mask_key_suffix",
    "PROVIDER_QUALITY_SCORES",
]
