# feedback_trust_provenance.py
# Schema and verification logic for Feedback Trust Provenance

import os
from datetime import datetime, timezone
from typing import Optional

try:
    from backend.security_utils import extract_bearer_token
except ImportError:
    from security_utils import extract_bearer_token

try:
    import backend.main as backend_main
except ImportError:
    try:
        import main as backend_main
    except ImportError:
        backend_main = None

from typing import Optional, Literal

# Trust Levels
TRUST_AUTHOR = "author"
TRUST_SYSTEM = "system"
TRUST_TRUSTED_READER = "trusted_reader"
TRUST_READER = "reader"
TRUST_ANONYMOUS = "anonymous"

# Allowlisted methods for elevated trust
ALLOWLISTED_VERIFICATION_METHODS = {
    "jwt_author_profile",
    "jwt_trusted_reader_profile",
    "internal_backend_cron",
    "internal_backend_canary"
}

def determine_provenance(
    authorization: Optional[str],
    client_source: Optional[str] = None,
    *,
    caller_context: Literal["public", "authenticated_public", "internal_system", "internal_canary"]
) -> dict:
    """
    Determine trust provenance based on server-side JWT authentication verification.
    """
    # Fail-closed for malformed or invalid context
    valid_contexts = ["public", "authenticated_public", "internal_system", "internal_canary"]
    if caller_context not in valid_contexts:
        return {
            "trust_level": TRUST_ANONYMOUS,
            "trust_verified": False,
            "trust_verification_method": "none",
            "trust_verified_at": None,
            "trust_subject_user_id": None,
            "source": "anonymous_feedback",
            "source_verified": False,
            "is_author": False,
            "is_trusted_reader": False
        }

    token = extract_bearer_token(authorization) if authorization else None

    # Strict restrictions on privileged sources
    # - Only internal_canary can produce system_canary
    if client_source == "system_canary" and caller_context != "internal_canary":
        client_source = "anonymous_feedback"

    # - Only internal_system can produce system_detected_failure
    if client_source == "system_detected_failure" and caller_context != "internal_system":
        client_source = "anonymous_feedback"

    # - Public routes cannot spoof author_feedback or system sources via string
    if caller_context in ["public", "authenticated_public"]:
        if client_source in ["system_canary", "system_detected_failure", "author_feedback"]:
            client_source = "anonymous_feedback"

    supabase = getattr(backend_main, "supabase", None) if backend_main else None

    # 1. If JWT is present, verify via Supabase Auth
    if token and supabase:
        try:
            user_resp = supabase.auth.get_user(token)
            if user_resp and user_resp.user:
                user_id = user_resp.user.id
                email = user_resp.user.email

                # Fetch profile role from database
                profile_resp = supabase.table("profiles").select("role").eq("id", user_id).execute()
                role = "reader"  # default
                if profile_resp.data:
                    role = profile_resp.data[0].get("role", "reader").lower()

                # Determine trust level and populate contract fields
                if role in ["author", "superadmin", "editor"]:
                    return {
                        "trust_level": TRUST_AUTHOR,
                        "trust_verified": True,
                        "trust_verification_method": "jwt_author_profile",
                        "trust_verified_at": datetime.now(timezone.utc).isoformat(),
                        "trust_subject_user_id": user_id,
                        "source": "author_feedback",
                        "source_verified": True,
                        "is_author": True,
                        "is_trusted_reader": True
                    }
                elif role == "trusted_reader":
                    return {
                        "trust_level": TRUST_TRUSTED_READER,
                        "trust_verified": True,
                        "trust_verification_method": "jwt_trusted_reader_profile",
                        "trust_verified_at": datetime.now(timezone.utc).isoformat(),
                        "trust_subject_user_id": user_id,
                        "source": client_source or "trusted_reader_feedback",
                        "source_verified": True,
                        "is_author": False,
                        "is_trusted_reader": True
                    }
                else:  # reader
                    return {
                        "trust_level": TRUST_READER,
                        "trust_verified": True,
                        "trust_verification_method": "jwt_reader_profile",
                        "trust_verified_at": datetime.now(timezone.utc).isoformat(),
                        "trust_subject_user_id": user_id,
                        "source": client_source or "reader_feedback",
                        "source_verified": True,
                        "is_author": False,
                        "is_trusted_reader": False
                    }
        except Exception:
            pass

    # 2. Anonymous submission
    return {
        "trust_level": TRUST_ANONYMOUS,
        "trust_verified": False,
        "trust_verification_method": "none",
        "trust_verified_at": None,
        "trust_subject_user_id": None,
        "source": client_source or "anonymous_feedback",
        "source_verified": False,
        "is_author": False,
        "is_trusted_reader": False
    }

def get_system_provenance() -> dict:
    """
    Get trusted system provenance configuration for background cron or script detection.
    """
    return {
        "trust_level": TRUST_SYSTEM,
        "trust_verified": True,
        "trust_verification_method": "internal_backend_cron",
        "trust_verified_at": datetime.now(timezone.utc).isoformat(),
        "trust_subject_user_id": None,
        "source": "system_detected_failure",
        "source_verified": True,
        "is_author": False,
        "is_trusted_reader": False
    }

def get_canary_provenance() -> dict:
    """
    Get trusted system canary provenance configuration for system canary scripts.
    """
    return {
        "trust_level": TRUST_SYSTEM,
        "trust_verified": True,
        "trust_verification_method": "internal_backend_canary",
        "trust_verified_at": datetime.now(timezone.utc).isoformat(),
        "trust_subject_user_id": None,
        "source": "system_canary",
        "source_verified": True,
        "is_author": False,
        "is_trusted_reader": False
    }
