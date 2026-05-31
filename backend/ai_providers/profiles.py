"""
Provider profile definitions and config normalization.

Defines the default free-tier AI providers (NO Gemini, NO Google Translate)
and provides utilities to build runtime profiles from Supabase config.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item for item in (_normalize_text(value) for value in values) if item]


def mask_key_suffix(raw: str) -> str:
    """Mask an API key for display, showing only the last 4 chars."""
    token = _normalize_text(raw)
    if not token:
        return ""
    if len(token) <= 4:
        return "***"
    return f"****{token[-4:]}"


@dataclass
class ProviderProfile:
    """Runtime profile for a single AI provider."""

    name: str
    display_name: str
    provider_type: str  # "openai_compatible" | "cloudflare" | "huggingface"
    enabled: bool
    base_url: str = ""
    api_key_pool: list[str] = field(default_factory=list)
    model_pool: list[str] = field(default_factory=list)
    timeout: int = 20
    default_model: str = ""

    def normalized(self) -> "ProviderProfile":
        """Return a clean copy with trimmed strings and valid defaults."""
        return ProviderProfile(
            name=_normalize_text(self.name).lower(),
            display_name=_normalize_text(self.display_name)
            or _normalize_text(self.name),
            provider_type=_normalize_text(self.provider_type).lower(),
            enabled=bool(self.enabled),
            base_url=_normalize_text(self.base_url),
            api_key_pool=_normalize_string_list(self.api_key_pool),
            model_pool=_normalize_string_list(self.model_pool),
            timeout=max(1, int(self.timeout or 20)),
            default_model=_normalize_text(self.default_model),
        )

    def to_public_dict(self) -> dict[str, Any]:
        """Serialize for API responses (keys redacted)."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "type": self.provider_type,
            "enabled": self.enabled,
            "base_url": self.base_url,
            "api_keys": [mask_key_suffix(key) for key in self.api_key_pool],
            "models": list(self.model_pool),
            "default_model": self.default_model
            or (self.model_pool[0] if self.model_pool else ""),
            "timeout": self.timeout,
        }


def get_default_provider_profiles() -> dict[str, dict[str, Any]]:
    """Default provider catalog — NO Gemini, NO Google Translate.

    All providers use the OpenAI-compatible chat/completions API.
    Free-tier keys can be obtained from each provider's website.
    """
    return {
        "groq": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_keys": [],
            "models": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ],
            "timeout": 20,
        },
        "cerebras": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "Cerebras",
            "base_url": "https://api.cerebras.ai/v1",
            "api_keys": [],
            "models": ["llama3.1-8b", "llama3.1-70b"],
            "timeout": 20,
        },
        "openrouter": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "OpenRouter",
            "base_url": "https://openrouter.ai/api/v1",
            "api_keys": [],
            "models": [
                "meta-llama/llama-3.3-70b-instruct:free",
                "meta-llama/llama-3.2-3b-instruct:free",
            ],
            "timeout": 25,
        },
        "mistral": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "Mistral AI",
            "base_url": "https://api.mistral.ai/v1",
            "api_keys": [],
            "models": ["mistral-small-latest", "mistral-tiny"],
            "timeout": 20,
        },
        "sambanova": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "SambaNova",
            "base_url": "https://api.sambanova.ai/v1",
            "api_keys": [],
            "models": [
                "DeepSeek-V3.1",
                "Llama-4-Maverick-17B-128E-Instruct",
            ],
            "timeout": 25,
        },
        "github": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "GitHub Models",
            "base_url": "https://models.inference.ai.azure.com",
            "api_keys": [],
            "models": ["gpt-4o-mini", "meta-llama-3-8b-instruct"],
            "timeout": 20,
        },
        "ai21": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "AI21 Studio",
            "base_url": "https://api.ai21.com/studio/v1",
            "api_keys": [],
            "models": ["jamba-1.5-mini"],
            "timeout": 20,
        },
        "deepseek": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "api_keys": [],
            "models": ["deepseek-chat"],
            "timeout": 25,
        },
        "nvidia_nim": {
            "enabled": False,
            "type": "openai_compatible",
            "display_name": "NVIDIA NIM",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "api_keys": [],
            "models": ["meta/llama-3.1-8b-instruct"],
            "timeout": 20,
        },
    }


# Quality scores for dynamic ranking (higher = better translation quality)
PROVIDER_QUALITY_SCORES: dict[str, float] = {
    "openrouter": 8.5,
    "groq": 8.0,
    "cerebras": 7.5,
    "sambanova": 7.5,
    "github": 7.5,
    "mistral": 7.5,
    "ai21": 7.0,
    "deepseek": 8.0,
    "nvidia_nim": 7.5,
}


def build_provider_profiles(
    config_data: dict[str, Any],
) -> dict[str, ProviderProfile]:
    """Build normalized ProviderProfile instances from Supabase config JSON.

    Args:
        config_data: The `ai_provider_config.providers` dict from Supabase,
                     or the full `ai_provider_config` dict.

    Returns:
        Dict of provider_name -> ProviderProfile.
    """
    providers_raw = config_data.get("providers", config_data)
    if not isinstance(providers_raw, dict):
        return {}

    defaults = get_default_provider_profiles()
    profiles: dict[str, ProviderProfile] = {}

    for provider_name, provider_data in providers_raw.items():
        if not isinstance(provider_data, dict):
            continue

        # Merge with defaults for base_url, models, etc.
        default = defaults.get(provider_name, {})
        provider_type = _normalize_text(
            provider_data.get("type", default.get("type", "openai_compatible"))
        ).lower()
        base_url = _normalize_text(
            provider_data.get("base_url", default.get("base_url", ""))
        )
        api_keys = _normalize_string_list(provider_data.get("api_keys", []))
        models = _normalize_string_list(
            provider_data.get("models", default.get("models", []))
        )
        default_model = _normalize_text(
            provider_data.get(
                "default_model", default.get("default_model", "")
            )
        )
        timeout = max(
            1,
            int(
                provider_data.get("timeout", default.get("timeout", 20)) or 20
            ),
        )

        if not default_model and models:
            default_model = models[0]

        # Ensure default model is at the front
        if default_model:
            if default_model in models:
                models = [default_model] + [
                    m for m in models if m != default_model
                ]
            else:
                models = [default_model] + models

        profiles[provider_name] = ProviderProfile(
            name=provider_name,
            display_name=_normalize_text(
                provider_data.get(
                    "display_name", default.get("display_name", provider_name)
                )
            )
            or provider_name,
            provider_type=provider_type,
            enabled=bool(provider_data.get("enabled", False)),
            base_url=base_url,
            api_key_pool=api_keys,
            model_pool=models,
            timeout=timeout,
            default_model=default_model or (models[0] if models else ""),
        ).normalized()

    return profiles
