"""
Async provider health checker.

Tests connectivity and model responsiveness for configured providers.
Used by admin endpoints and startup health probes.
"""

from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from ai_providers.base import AIRequest, AIResult
from ai_providers.error_classifier import classify_error
from ai_providers.openai_compatible import OpenAICompatibleProvider
from ai_providers.profiles import ProviderProfile, build_provider_profiles
from ai_providers.router import ProviderRouter


STATUS_MESSAGES = {
    "ok": "Kết nối thành công! Hoạt động hoàn hảo.",
    "missing_key": "Thiếu API Key hoặc khóa chưa được cấu hình.",
    "auth_error": "Lỗi xác thực (API Key không hợp lệ hoặc đã bị hủy).",
    "quota_or_rate_limited": "Hết hạn mức gọi API (Quota Exceeded / Rate Limited).",
    "model_not_found": "Mô hình (Model ID) không tồn tại hoặc không được hỗ trợ.",
    "endpoint_not_found": "Sai URL/Endpoint hoặc đường dẫn API không khả dụng.",
    "payload_error": "Tham số hoặc dữ liệu gửi đi không được chấp nhận.",
    "timeout": "Thời gian phản hồi quá lâu (Timeout).",
    "network_error": "Lỗi mạng hoặc không thể kết nối tới máy chủ.",
    "provider_disabled": "Nhà cung cấp hiện đang bị tắt trong cài đặt.",
    "cancelled": "Yêu cầu kiểm tra đã bị dừng.",
    "unsupported": "Phương thức kiểm tra chưa được hỗ trợ cho nhà cung cấp này.",
    "unknown_error": "Lỗi chưa phân loại.",
}

SUGGESTIONS = {
    "ok": "Sẵn sàng sử dụng.",
    "missing_key": "Vui lòng thêm API key cho nhà cung cấp này trong cài đặt.",
    "auth_error": "Kiểm tra lại API Key có bị thừa khoảng trắng không, hoặc tạo key mới.",
    "quota_or_rate_limited": "Đợi 1 phút để reset giới hạn RPM, hoặc thêm providers khác.",
    "model_not_found": "Kiểm tra lại Model ID trong cấu hình.",
    "endpoint_not_found": "Kiểm tra lại Base URL trong cấu hình.",
    "payload_error": "Kiểm tra cấu hình hoặc tham số gửi đi.",
    "timeout": "Kiểm tra đường truyền mạng.",
    "network_error": "Kiểm tra kết nối internet hoặc Base URL.",
    "provider_disabled": "Bật nhà cung cấp trong cài đặt.",
    "cancelled": "Bạn đã dừng kiểm tra.",
    "unsupported": "Liên hệ tác giả để cập nhật.",
    "unknown_error": "Kiểm tra chi tiết lỗi hoặc thử lại sau.",
}


def _classify_health_error(error_type_str: str) -> str:
    """Map error_classifier result to health status category."""
    mapping = {
        "auth_failure": "auth_error",
        "quota_rate_limit": "quota_or_rate_limited",
        "token_limit": "quota_or_rate_limited",
        "timeout": "timeout",
        "transport_error": "network_error",
        "unknown_transport_error": "network_error",
        "model_error": "model_not_found",
        "model_unavailable": "model_not_found",
        "provider_5xx": "network_error",
    }
    return mapping.get(error_type_str, "unknown_error")


@dataclass
class ProviderHealthResult:
    """Result of a health check for one provider+model."""

    provider_id: str
    provider_name: str
    model_id: str
    status: str
    error_category: str
    message: str
    latency_ms: int = 0
    checked_at: str = field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    suggestion: str = ""
    raw_error_sanitized: str = ""


class ProviderHealthChecker:
    """Check connectivity and model responsiveness for providers."""

    def __init__(
        self,
        provider_router: Optional[ProviderRouter] = None,
    ):
        self.provider_router = provider_router

    async def check_provider(
        self,
        profile: ProviderProfile,
        model_id: Optional[str] = None,
    ) -> ProviderHealthResult:
        """Check connection for a provider using its default or specified model."""

        check_model = model_id or profile.default_model or (
            profile.model_pool[0] if profile.model_pool else ""
        )

        if not check_model:
            return ProviderHealthResult(
                provider_id=profile.name,
                provider_name=profile.display_name,
                model_id="",
                status="model_not_found",
                error_category="no_model_configured",
                message=STATUS_MESSAGES["model_not_found"],
                suggestion=SUGGESTIONS["model_not_found"],
            )

        if not profile.api_key_pool:
            return ProviderHealthResult(
                provider_id=profile.name,
                provider_name=profile.display_name,
                model_id=check_model,
                status="missing_key",
                error_category="missing_key",
                message=STATUS_MESSAGES["missing_key"],
                suggestion=SUGGESTIONS["missing_key"],
            )

        # Build a temporary profile for the check
        temp_profile = ProviderProfile(
            name=profile.name,
            display_name=profile.display_name,
            provider_type=profile.provider_type,
            enabled=True,
            base_url=profile.base_url,
            api_key_pool=profile.api_key_pool,
            model_pool=[check_model],
            timeout=10,  # Short timeout for diagnostics
            default_model=check_model,
        ).normalized()

        provider_instance = OpenAICompatibleProvider(profile=temp_profile)

        request = AIRequest(
            text="Health check: respond with 'OK' in one word.",
            mode="chat",
            max_output_tokens=32,
            temperature=0.0,
        )

        started = time.time()
        try:
            result = await provider_instance.call(request)
            latency = round((time.time() - started) * 1000)

            if result.status == "success":
                self._update_router_health(profile.name, check_model, result)
                return ProviderHealthResult(
                    provider_id=profile.name,
                    provider_name=profile.display_name,
                    model_id=check_model,
                    status="ok",
                    error_category="",
                    message=STATUS_MESSAGES["ok"],
                    latency_ms=latency,
                    suggestion=SUGGESTIONS["ok"],
                )

            err_cat = _classify_health_error(result.error_type)
            self._update_router_health(profile.name, check_model, result)
            return ProviderHealthResult(
                provider_id=profile.name,
                provider_name=profile.display_name,
                model_id=check_model,
                status=err_cat,
                error_category=result.error_type,
                message=STATUS_MESSAGES.get(err_cat, STATUS_MESSAGES["unknown_error"]),
                latency_ms=latency,
                suggestion=SUGGESTIONS.get(err_cat, SUGGESTIONS["unknown_error"]),
                raw_error_sanitized=result.error_message,
            )
        except Exception as exc:
            latency = round((time.time() - started) * 1000)
            err_type = classify_error(exc)
            err_cat = _classify_health_error(err_type)
            return ProviderHealthResult(
                provider_id=profile.name,
                provider_name=profile.display_name,
                model_id=check_model,
                status=err_cat,
                error_category=err_type,
                message=STATUS_MESSAGES.get(err_cat, STATUS_MESSAGES["unknown_error"]),
                latency_ms=latency,
                suggestion=SUGGESTIONS.get(err_cat, SUGGESTIONS["unknown_error"]),
                raw_error_sanitized=str(exc),
            )

    async def check_all_configured(
        self,
        config_data: dict[str, Any],
        limit_per_provider: Optional[int] = 1,
    ) -> list[ProviderHealthResult]:
        """Check all enabled providers from config."""
        profiles = build_provider_profiles(config_data)
        results: list[ProviderHealthResult] = []

        for provider_id, profile in profiles.items():
            if not profile.enabled:
                continue

            models = list(profile.model_pool)
            if limit_per_provider and len(models) > limit_per_provider:
                models = models[:limit_per_provider]

            if not models:
                results.append(await self.check_provider(profile))
            else:
                for model_id in models:
                    results.append(
                        await self.check_provider(profile, model_id=model_id)
                    )

        return results

    def _update_router_health(
        self,
        provider_id: str,
        model_id: str,
        result: AIResult,
    ) -> None:
        """Keep router state in sync with health check results."""
        if not self.provider_router:
            return

        try:
            key_index = result.key_index if result.key_index >= 0 else None
            key_id = result.key_id if result.key_id else None

            if result.status == "success":
                self.provider_router.mark_success(
                    provider_id,
                    model_id,
                    result.latency_ms,
                    key_index=key_index,
                    key_id=key_id,
                    display_name=provider_id.upper(),
                )
            else:
                self.provider_router.mark_failure(
                    provider_id,
                    model_id,
                    result.error_type or "health_check_failed",
                    result.latency_ms,
                    key_index=key_index,
                    key_id=key_id,
                    display_name=provider_id.upper(),
                )
        except Exception:
            pass
