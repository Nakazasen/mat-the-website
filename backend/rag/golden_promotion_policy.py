# golden_promotion_policy.py
# Trust weights, score thresholds, mapping, and constraint parsing logic

import re
import json

# Trust levels
TRUST_AUTHOR = "author"
TRUST_SYSTEM = "system"
TRUST_TRUSTED_READER = "trusted_reader"
TRUST_READER = "reader"
TRUST_ANONYMOUS = "anonymous"

# Threshold required to auto-promote a candidate
SCORE_THRESHOLD = 1.0

# Trust scores contributed by a single feedback item
TRUST_WEIGHTS = {
    TRUST_AUTHOR: 1.0,           # Instant promotion
    TRUST_SYSTEM: 1.0,           # Instant promotion
    TRUST_TRUSTED_READER: 0.5,   # Needs 2 signals
    TRUST_READER: 0.34,          # Needs 3 signals (quorum)
    TRUST_ANONYMOUS: 0.2         # Needs 5 signals
}

def determine_trust_level(feedback):
    """
    Determine trust level based on secure server-side metadata fields only.
    """
    trust_verified = feedback.get("trust_verified") is True or feedback.get("trust_verified") == "true"
    source_verified = feedback.get("source_verified") is True or feedback.get("source_verified") == "true"
    method = feedback.get("trust_verification_method")

    # Author
    is_author_claim = (
        feedback.get("source") == "author_feedback" or
        feedback.get("trust_level") == "author" or
        feedback.get("is_author") is True or
        feedback.get("is_author") == "true"
    )
    if is_author_claim and trust_verified and method == "jwt_author_profile":
        return TRUST_AUTHOR

    # System
    is_system_claim = (
        feedback.get("source") == "system_detected_failure" or
        feedback.get("trust_level") == "system"
    )
    if is_system_claim and (trust_verified or source_verified) and method == "internal_backend_cron":
        return TRUST_SYSTEM

    # Trusted Reader
    is_trusted_claim = (
        feedback.get("trust_level") == "trusted_reader" or
        feedback.get("is_trusted_reader") is True or
        feedback.get("is_trusted_reader") == "true"
    )
    if is_trusted_claim and trust_verified and method == "jwt_trusted_reader_profile":
        return TRUST_TRUSTED_READER

    # Reader
    is_reader_claim = (
        feedback.get("trust_level") == "reader"
    )
    if is_reader_claim and trust_verified and method == "jwt_reader_profile":
        return TRUST_READER

    return TRUST_ANONYMOUS

def parse_constraints_from_comment(user_comment, suggested_correction):
    """
    Parse constraints from user comments or suggested corrections.
    Looks for patterns like:
      must_not_contain: ["term1", "term2"]
      forbidden_patterns: ["pattern1", "pattern2"]
      required_terms: ["term3"]
      expected_abstain: "abstain text"
    """
    full_text = f"{user_comment or ''}\n{suggested_correction or ''}"

    must_not_contain = []
    semantic_forbidden_patterns = []
    semantic_required_any_terms = []
    expected_abstain_text = ""

    # Parse JSON-like arrays
    not_contain_match = re.search(r"must_not_contain\s*:\s*(\[[^\]]*\])", full_text, re.IGNORECASE)
    if not_contain_match:
        try:
            must_not_contain = json.loads(not_contain_match.group(1))
        except Exception:
            pass

    forbidden_match = re.search(r"forbidden_patterns\s*:\s*(\[[^\]]*\])", full_text, re.IGNORECASE)
    if forbidden_match:
        try:
            semantic_forbidden_patterns = json.loads(forbidden_match.group(1))
        except Exception:
            pass

    required_match = re.search(r"required_terms\s*:\s*(\[[^\]]*\])", full_text, re.IGNORECASE)
    if required_match:
        try:
            semantic_required_any_terms = json.loads(required_match.group(1))
        except Exception:
            pass

    abstain_match = re.search(r"expected_abstain\s*:\s*\"([^\"]*)\"", full_text, re.IGNORECASE)
    if not abstain_match:
        abstain_match = re.search(r"expected_abstain\s*:\s*'([^']*)'", full_text, re.IGNORECASE)
    if abstain_match:
        expected_abstain_text = abstain_match.group(1)

    return must_not_contain, semantic_forbidden_patterns, semantic_required_any_terms, expected_abstain_text
