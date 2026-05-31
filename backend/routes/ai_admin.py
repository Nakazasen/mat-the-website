"""
Admin API for AI provider management.

Endpoints:
- GET  /api/admin/ai/providers       - List all configured providers + health status
- PUT  /api/admin/ai/providers       - Update provider config
- POST /api/admin/ai/providers/health-check - Run health check
- GET  /api/admin/ai/providers/health-snapshot - Runtime health state
- POST /api/admin/ai/providers/reset-cooldowns - Clear all cooldowns
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin/ai", tags=["ai_admin"])
logger = logging.getLogger(__name__)


class ProviderConfigResponse(BaseModel):
    providers: dict[str, Any]
    translation_policy: dict[str, Any]
    chat_policy: dict[str, Any]


class ProviderListItem(BaseModel):
    name: str
    display_name: str
    type: str
    enabled: bool
    base_url: str
    api_keys: list[str]
    models: list[str]
    default_model: str
    timeout: int


class ProviderListResponse(BaseModel):
    providers: list[ProviderListItem]
    total: int


class UpdateProviderConfigRequest(BaseModel):
    providers: Optional[dict[str, Any]] = None
    translation_policy: Optional[dict[str, Any]] = None
    chat_policy: Optional[dict[str, Any]] = None


class UpdateProviderConfigResponse(BaseModel):
    status: str
    detail: str


class HealthCheckRequest(BaseModel):
    provider_id: Optional[str] = None
    model_id: Optional[str] = None


class HealthCheckResultItem(BaseModel):
    provider_id: str
    provider_name: str
    model_id: str
    status: str
    error_category: str
    message: str
    latency_ms: int
    checked_at: str
    suggestion: str
    raw_error_sanitized: str


class HealthCheckResponse(BaseModel):
    results: list[HealthCheckResultItem]
    total: int


class HealthSnapshotItem(BaseModel):
    provider_name: str
    display_name: str
    model: str
    is_available: bool
    health_status: str
    consecutive_failures: int
    success_count: int
    failure_count: int
    last_error_type: str
    last_latency_ms: int
    quality_score: float
    latency_score: float


class HealthSnapshotResponse(BaseModel):
    snapshot: list[HealthSnapshotItem]
    total: int


class ResetCooldownsResponse(BaseModel):
    status: str
    detail: str


def _get_supabase():
    try:
        from main import supabase
    except ImportError:
        from backend.main import supabase
    return supabase


def _get_admin_deps():
    try:
        from main import (
            supabase,
            verify_admin,
            get_provider_router,
            get_provider_health_checker,
            resolve_ai_provider_config,
            build_provider_router_from_config,
            build_provider_profiles,
        )
    except ImportError:
        from backend.main import (
            supabase,
            verify_admin,
            get_provider_router,
            get_provider_health_checker,
            resolve_ai_provider_config,
            build_provider_router_from_config,
            build_provider_profiles,
        )
    return {
        "supabase": supabase,
        "verify_admin": verify_admin,
        "get_provider_router": get_provider_router,
        "get_provider_health_checker": get_provider_health_checker,
        "resolve_ai_provider_config": resolve_ai_provider_config,
        "build_provider_router_from_config": build_provider_router_from_config,
        "build_provider_profiles": build_provider_profiles,
    }


async def _require_superadmin(authorization: Optional[str]) -> dict:
    deps = _get_admin_deps()
    user = await deps["verify_admin"](authorization)
    if user.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can manage AI providers.")
    return user


@router.get("/providers", response_model=ProviderListResponse)
async def list_providers(authorization: Optional[str] = Header(None)):
    """List all configured providers with their profiles (keys redacted)."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    config = deps["resolve_ai_provider_config"]()
    profiles = deps["build_provider_profiles"](config)

    items = []
    for name, profile in profiles.items():
        items.append(
            ProviderListItem(**profile.to_public_dict())
        )

    return ProviderListResponse(providers=items, total=len(items))


@router.get("/providers/config", response_model=ProviderConfigResponse)
async def get_provider_config(authorization: Optional[str] = Header(None)):
    """Get the full provider config (keys redacted)."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    config = deps["resolve_ai_provider_config"]()
    profiles = deps["build_provider_profiles"](config)

    sanitized_providers = {}
    for name, profile in profiles.items():
        sanitized_providers[name] = profile.to_public_dict()

    return ProviderConfigResponse(
        providers=sanitized_providers,
        translation_policy=config.get("translation_policy", {"mode": "waterfall"}),
        chat_policy=config.get("chat_policy", {"mode": "waterfall"}),
    )


@router.put("/providers", response_model=UpdateProviderConfigResponse)
async def update_provider_config(
    body: UpdateProviderConfigRequest,
    authorization: Optional[str] = Header(None),
):
    """Update the ai_provider_config in novel_settings."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    supabase = deps["supabase"]

    # Load current config
    current_config = deps["resolve_ai_provider_config"]()

    # Merge updates
    if body.providers is not None:
        current_providers = current_config.get("providers", {})
        for provider_name, provider_data in body.providers.items():
            if not isinstance(provider_data, dict):
                continue
            if provider_name not in current_providers:
                current_providers[provider_name] = {}
            
            # Special secure handling for api_keys:
            # If the client sends an "api_keys" list, we must preserve any existing keys
            # that were sent back as masked placeholders (e.g., starting with "****" or "[REDACTED")
            if "api_keys" in provider_data and isinstance(provider_data["api_keys"], list):
                incoming_keys = provider_data["api_keys"]
                existing_keys = current_providers.get(provider_name, {}).get("api_keys", [])
                if not isinstance(existing_keys, list):
                    existing_keys = []
                
                merged_keys = []
                for i, incoming_key in enumerate(incoming_keys):
                    incoming_key_str = str(incoming_key).strip()
                    if (incoming_key_str.startswith("****") or incoming_key_str.startswith("[REDACTED")) and i < len(existing_keys):
                        merged_keys.append(existing_keys[i])
                    else:
                        merged_keys.append(incoming_key_str)
                provider_data["api_keys"] = [k for k in merged_keys if k]

            current_providers[provider_name].update(provider_data)
        current_config["providers"] = current_providers

    if body.translation_policy is not None:
        current_config["translation_policy"] = body.translation_policy

    if body.chat_policy is not None:
        current_config["chat_policy"] = body.chat_policy

    # Save to Supabase
    try:
        supabase.table("novel_settings").update(
            {"ai_provider_config": current_config}
        ).eq("id", 1).execute()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save provider config: {exc}",
        )

    # Rebuild the router with new config
    try:
        deps["build_provider_router_from_config"](
            config_data=current_config, force_rebuild=True
        )
    except Exception as exc:
        logger.warning(f"Failed to rebuild provider router: {exc}")

    return UpdateProviderConfigResponse(
        status="ok",
        detail="Provider config updated and router rebuilt.",
    )


@router.post("/providers/health-check", response_model=HealthCheckResponse)
async def run_health_check(
    body: HealthCheckRequest = HealthCheckRequest(),
    authorization: Optional[str] = Header(None),
):
    """Run health check for one or all providers."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    config = deps["resolve_ai_provider_config"]()
    checker = deps["get_provider_health_checker"]()

    if body.provider_id:
        profiles = deps["build_provider_profiles"](config)
        profile = profiles.get(body.provider_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{body.provider_id}' not found in config.",
            )
        result = await checker.check_provider(profile, model_id=body.model_id)
        items = [
            HealthCheckResultItem(
                provider_id=result.provider_id,
                provider_name=result.provider_name,
                model_id=result.model_id,
                status=result.status,
                error_category=result.error_category,
                message=result.message,
                latency_ms=result.latency_ms,
                checked_at=result.checked_at,
                suggestion=result.suggestion,
                raw_error_sanitized=result.raw_error_sanitized,
            )
        ]
    else:
        raw_results = await checker.check_all_configured(config)
        items = [
            HealthCheckResultItem(
                provider_id=r.provider_id,
                provider_name=r.provider_name,
                model_id=r.model_id,
                status=r.status,
                error_category=r.error_category,
                message=r.message,
                latency_ms=r.latency_ms,
                checked_at=r.checked_at,
                suggestion=r.suggestion,
                raw_error_sanitized=r.raw_error_sanitized,
            )
            for r in raw_results
        ]

    return HealthCheckResponse(results=items, total=len(items))


@router.get("/providers/health-snapshot", response_model=HealthSnapshotResponse)
async def get_health_snapshot(authorization: Optional[str] = Header(None)):
    """Get current runtime health state for all tracked providers."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    router_instance = deps["get_provider_router"]()
    raw_snapshot = router_instance.get_health_snapshot()

    items = [
        HealthSnapshotItem(
            provider_name=s.get("provider_name", ""),
            display_name=s.get("display_name", ""),
            model=s.get("model", ""),
            is_available=s.get("is_available", False),
            health_status=s.get("health_status", "unknown"),
            consecutive_failures=s.get("consecutive_failures", 0),
            success_count=s.get("success_count", 0),
            failure_count=s.get("failure_count", 0),
            last_error_type=s.get("last_error_type", ""),
            last_latency_ms=s.get("last_latency_ms", 0),
            quality_score=s.get("quality_score", 5.0),
            latency_score=s.get("latency_score", 0.0),
        )
        for s in raw_snapshot
    ]

    return HealthSnapshotResponse(snapshot=items, total=len(items))


@router.post("/providers/reset-cooldowns", response_model=ResetCooldownsResponse)
async def reset_cooldowns(authorization: Optional[str] = Header(None)):
    """Clear all provider cooldowns and restore availability."""
    await _require_superadmin(authorization)
    deps = _get_admin_deps()
    router_instance = deps["get_provider_router"]()
    router_instance.reset_cooldowns()

    return ResetCooldownsResponse(
        status="ok",
        detail="All provider cooldowns have been cleared.",
    )
