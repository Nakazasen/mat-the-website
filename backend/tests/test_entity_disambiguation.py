import os
import sys
import json
import pytest
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.rag.entity_disambiguation import (
    classify_entity_candidate,
    detect_false_positive_type,
    build_entity_disambiguation_plan
)

def test_entity_disambiguation_rules():
    # 1. "Zombie Cấp 3" -> zombie_species
    res = classify_entity_candidate("Zombie Cấp 3", current_type="entity")
    assert res["target_type"] == "zombie_species"
    assert res["action"] == "update_type"

    # 2. "Tinh thể zombie" -> crystal_core
    res = classify_entity_candidate("Tinh thể zombie", current_type="entity")
    assert res["target_type"] == "crystal_core"
    assert res["action"] == "update_type"

    # 3. "Căn cứ Hi Vọng" -> location_base
    res = classify_entity_candidate("Căn cứ Hi Vọng", current_type="entity")
    assert res["target_type"] == "location_base"
    assert res["action"] == "update_type"

    # 4. "Đại Thiên Thần" -> organization_faction
    res = classify_entity_candidate("Đại Thiên Thần", current_type="entity")
    assert res["target_type"] == "organization_faction"
    assert res["action"] == "update_type"

    # 5. "Băng Độc" -> ability_skill
    res = classify_entity_candidate("Băng Độc", current_type="entity")
    assert res["target_type"] == "ability_skill"
    assert res["action"] == "update_type"

    # 6. "đoàn đội" -> noise_candidate hoặc manual_review, không auto organization_faction
    res = classify_entity_candidate("đoàn đội", current_type="entity")
    assert res["action"] == "noise_candidate"
    assert res["target_type"] == "entity"

    # 7. "đoàn ô" -> noise_candidate hoặc manual_review, không auto organization_faction
    res = classify_entity_candidate("đoàn ô", current_type="entity")
    assert res["action"] == "noise_candidate"
    assert res["target_type"] == "entity"

    # 8. Generic title-case unknown không auto character bừa
    res = classify_entity_candidate("Tiêu Minh", current_type="entity")
    assert res["action"] == "manual_review"
    assert res["target_type"] == "entity"

def test_false_positive_reversion():
    # Organization false positives "đoàn đội", "đoàn ô" should revert/mark noise
    res = classify_entity_candidate("đoàn đội", current_type="organization_faction")
    assert res["target_type"] == "entity"
    assert res["action"] == "noise_candidate"

    res = classify_entity_candidate("đoàn ô", current_type="organization_faction")
    assert res["target_type"] == "entity"
    assert res["action"] == "noise_candidate"

    # Location false positives like "Áo Khoác Phòng Hộ" (clothes) -> entity
    res = classify_entity_candidate("Áo Khoác Phòng Hộ", current_type="location_base")
    assert res["target_type"] == "entity"
    assert res["action"] == "update_type"

    # Character false positives with action words (e.g. "Hàn Phong đang") -> entity
    res = classify_entity_candidate("Hàn Phong đang", current_type="character")
    assert res["target_type"] == "entity"
    assert res["action"] == "update_type"

def test_dry_run_no_database_write(monkeypatch):
    # 9. Dry-run không ghi DB
    import backend.scripts.apply_entity_disambiguation_plan as applicator

    called_update = False

    class MockExecuteResult:
        def __init__(self, data):
            self.data = data

    class MockQuery:
        def __init__(self, data=None):
            self.data = data or []

        def select(self, *args, **kwargs):
            return self

        def range(self, *args, **kwargs):
            return self

        def update(self, *args, **kwargs):
            nonlocal called_update
            called_update = True
            return self

        def eq(self, *args, **kwargs):
            return self

        def execute(self):
            return MockExecuteResult(self.data)

    class MockSupabaseClient:
        def table(self, table_name):
            assert table_name in ("provisional_library", "oracle_cache")
            mock_data = [
                {"id": "rec1", "confidence": 1.0},
                {"id": "rec2", "confidence": 0.8}
            ]
            return MockQuery(mock_data)

    monkeypatch.setattr(applicator, "supabase", MockSupabaseClient())

    # Create a dummy plan file in memory or local path
    dummy_plan = {
        "to_update_type": [{"id": "rec1", "name": "Zombie Cấp 3", "old_type": "entity", "new_type": "zombie_species", "action": "update_type"}],
        "to_mark_manual_review": [{"id": "rec2", "name": "Đạo Tốc", "old_type": "entity", "new_type": "entity", "action": "manual_review"}],
        "to_mark_noise_candidate": []
    }
    
    plan_file = REPO_ROOT / "backend/rag/test_dummy_plan.json"
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(dummy_plan, f)

    try:
        sys.argv = ["apply_entity_disambiguation_plan.py", "--plan", str(plan_file)]
        applicator.main()
    except SystemExit as e:
        assert e.code == 0
    finally:
        if plan_file.exists():
            plan_file.unlink()

    assert not called_update, "Database was mutated during dry-run!"

def test_no_llm_no_embedding_codebase():
    # 10. Không LLM.
    # 11. Không embedding.
    target_files = [
        "backend/rag/entity_disambiguation.py",
        "backend/scripts/audit_entity_disambiguation.py",
        "backend/scripts/build_entity_disambiguation_plan.py",
        "backend/scripts/apply_entity_disambiguation_plan.py"
    ]
    for filename in target_files:
        path = REPO_ROOT / filename
        assert path.exists(), f"File {filename} does not exist"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            assert "openai" not in content, f"OpenAI reference found in {filename}"
            assert "anthropic" not in content, f"Anthropic reference found in {filename}"
            assert "cohere" not in content, f"Cohere reference found in {filename}"
            assert "llm" not in content, f"LLM reference found in {filename}"
            assert "embed" not in content, f"Embedding reference found in {filename}"
