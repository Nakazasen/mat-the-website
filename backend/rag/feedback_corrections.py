"""
RAG Feedback Corrections Module
Provides functionality to normalize, classify, and format admin-reviewed feedback into
correction drafts and evaluation cases.
"""

import re
from typing import Any, Dict, List, Optional

def normalize_feedback_for_correction(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Standardizes feedback fields to ensure correct types and presence of keys."""
    return {
        "id": str(feedback.get("id", "")),
        "question": str(feedback.get("question") or "").strip(),
        "answer": str(feedback.get("answer") or "").strip(),
        "source": str(feedback.get("source") or "").strip(),
        "citations": feedback.get("citations") or [],
        "chapter_progress": feedback.get("chapter_progress"),
        "feedback_type": str(feedback.get("feedback_type") or "other").strip(),
        "user_comment": str(feedback.get("user_comment") or "").strip(),
        "suggested_correction": str(feedback.get("suggested_correction") or "").strip(),
        "status": str(feedback.get("status") or "pending").strip(),
    }

def detect_entity_name(question: str, user_comment: str) -> Optional[str]:
    """Helper to detect characters, organizations, or key entities in feedback texts."""
    combined = f"{question} {user_comment}"
    if not combined.strip():
        return None

    # Check for known names case-insensitively
    known_entities = [
        "Hàn Phong", "Lâm Nhã Vy", "Trương Hạo", "Vương Mạnh",
        "Lý Đức", "Đại Thiên Thần", "Giang Thần"
    ]
    for ent in known_entities:
        if re.search(r'\b' + re.escape(ent) + r'\b', combined, re.IGNORECASE):
            return ent

    # Regex for sequences of capitalized Vietnamese words (e.g. Giang Thần, Hàn Quốc)
    # Match capitalized unicode words separated by spaces
    pattern = (
        r"\b([A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ]"
        r"[a-zà-ỹ]*+(?:\s+[A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤ"
        r"ƯỨỪỬỮỰÝỲỶỸỴ][a-zà-ỹ]*)+)\b"
    )
    matches = re.findall(pattern, combined)
    if matches:
        # Avoid common false positives
        for m in matches:
            if m.lower() not in ["tôi", "admin", "zombie", "rag", "oracle", "chương", "truyện"]:
                return m
    return None

def build_correction_draft_from_feedback(feedback: Dict[str, Any]) -> Dict[str, Any]:
    """Builds a rag_corrections draft from normalized feedback."""
    norm = normalize_feedback_for_correction(feedback)

    # 1. Detect entity name
    entity = detect_entity_name(norm["question"], norm["user_comment"])

    # 2. Map correction type based on feedback type
    fb_type = norm["feedback_type"]
    if fb_type == "wrong":
        # Check if it is a general wiki update or entity profile
        correction_type = "entity_profile" if entity else "wiki_update"
    elif fb_type == "spoiler":
        correction_type = "retrieval_rule"
    elif fb_type == "missing":
        correction_type = "entity_profile"
    elif fb_type == "hallucination":
        correction_type = "eval_case"
    else:
        correction_type = "other"

    # 3. Formulate proposed content
    sugg = norm["suggested_correction"]
    if sugg and sugg.lower() != "needs_review":
        proposed_content = sugg
    else:
        proposed_content = "needs_review"

    return {
        "feedback_id": norm["id"] if norm["id"] else None,
        "entity_name": entity,
        "correction_type": correction_type,
        "proposed_content": proposed_content,
        "evidence": norm["citations"],
        "status": "draft",
        "reviewer_note": "Generated from accepted/resolved feedback; human review required."
    }

def build_eval_case_from_feedback(feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Builds an evaluation case from normalized feedback, suitable for eval_cases.py."""
    norm = normalize_feedback_for_correction(feedback)
    if not norm["question"]:
        return None

    # 1. Determine ID
    fb_id = norm["id"]
    short_id = fb_id[:8] if len(fb_id) >= 8 else fb_id
    if not short_id:
        import uuid
        short_id = str(uuid.uuid4())[:8]

    # 2. Determine Intent
    fb_type = norm["feedback_type"]
    entity = detect_entity_name(norm["question"], norm["user_comment"])

    if fb_type == "spoiler":
        intent = "anti_spoiler"
    elif fb_type == "missing":
        intent = "no_data"
    elif entity:
        intent = "identity"
    else:
        intent = "event"

    # 3. expected_sources
    if intent == "identity":
        expected_sources = ["entity_context", "wiki_entries"]
    elif intent in ("anti_spoiler", "no_data"):
        expected_sources = ["story_chunks"]
    else:
        expected_sources = ["story_chunks"]

    # 4. must_include
    must_include = []
    if entity:
        must_include.append(entity)
    sugg = norm["suggested_correction"]
    if sugg and sugg.lower() != "needs_review":
        if len(sugg.split()) <= 4:
            must_include.append(sugg)
        else:
            # Extract capitalized keywords from suggested correction
            caps = re.findall(r"\b([A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ][a-zà-ỹ]*)\b", sugg)
            for cap in caps:
                if cap not in must_include and cap.lower() not in ["tôi", "admin", "zombie", "rag", "oracle"]:
                    must_include.append(cap)
    must_include = list(dict.fromkeys(must_include))[:5]

    # 5. must_not_include (extract from chatbot's wrong answer for hallucination/spoiler)
    must_not_include = []
    if fb_type in ("hallucination", "spoiler") and norm["answer"]:
        # Extract capitalized phrases or words from the incorrect answer
        caps = re.findall(r"\b([A-ZÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈÉẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ][a-zà-ỹ]*)\b", norm["answer"])
        for cap in caps:
            if cap not in must_not_include and cap.lower() not in ["tôi", "admin", "zombie", "rag", "oracle", "chương", "truyện"]:
                must_not_include.append(cap)
    must_not_include = list(dict.fromkeys(must_not_include))[:5]

    # 6. expected_chapters
    expected_chapters = []
    for cit in norm["citations"]:
        if isinstance(cit, dict):
            c_num = cit.get("chapter_number") or cit.get("chapter")
            if c_num is not None:
                try:
                    expected_chapters.append(int(c_num))
                except ValueError:
                    pass
    if not expected_chapters and norm["chapter_progress"] is not None:
        try:
            expected_chapters.append(int(norm["chapter_progress"]))
        except ValueError:
            pass
    expected_chapters = list(dict.fromkeys(expected_chapters))

    # 7. should_abstain
    should_abstain = (fb_type in ("spoiler", "missing"))

    return {
        "id": f"feedback_{short_id}",
        "question": norm["question"],
        "chapter_progress": norm["chapter_progress"] or 10,
        "intent": intent,
        "expected_sources": expected_sources,
        "must_include": must_include,
        "must_not_include": must_not_include,
        "expected_chapters": expected_chapters,
        "should_abstain": should_abstain,
        "notes": "Generated from feedback; human review required."
    }
