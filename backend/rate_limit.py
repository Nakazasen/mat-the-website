import threading
import time
from typing import Dict, Optional, Tuple

from fastapi import Request


class InMemoryCooldownLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_seen: Dict[str, float] = {}

    def allow(self, key: str, cooldown_seconds: int) -> Tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            last = self._last_seen.get(key)
            if last is not None:
                remaining = cooldown_seconds - int(now - last)
                if remaining > 0:
                    return False, remaining
            self._last_seen[key] = now
            if len(self._last_seen) > 50000:
                self._cleanup(now)
        return True, 0

    def _cleanup(self, now: float) -> None:
        cutoff = now - 3600
        stale_keys = [k for k, ts in self._last_seen.items() if ts < cutoff]
        for key in stale_keys:
            self._last_seen.pop(key, None)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
