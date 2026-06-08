import os
import sys
import pytest
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.rag.provisional_library_type_normalizer import (
    normalize_library_type,
    is_v2_type,
    build_type_normalization_plan
)

def test_normalization_rules():
    # 1. ability -> ability_skill
    assert normalize_library_type("Thao Túng Hàn Băng", "ability") == "ability_skill"
    assert normalize_library_type("Băng Độc", "ability") == "ability_skill"

    # 2. faction -> organization_faction
    assert normalize_library_type("Đại Thiên Thần", "faction") == "organization_faction"
    assert normalize_library_type("Tam Lang Hội", "faction") == "organization_faction"

    # 3. item "Tinh thể zombie" -> crystal_core
    assert normalize_library_type("Tinh thể zombie", "item") == "crystal_core"
    assert normalize_library_type("Tinh thạch khai phá", "item") == "crystal_core"
    assert normalize_library_type("Súng Diệt Quỷ", "item") == "item"  # no crystal keywords

    # 4. entity "Zombie Cấp 3" -> zombie_species
    assert normalize_library_type("Zombie Cấp 3", "entity") == "zombie_species"
    assert normalize_library_type("Xác sống biến dị", "entity") == "zombie_species"

    # 5. entity "Căn cứ Hi Vọng" -> location_base
    assert normalize_library_type("Căn cứ Hi Vọng", "entity") == "location_base"
    assert normalize_library_type("Vùng an toàn số 4", "entity") == "location_base"

    # 6. entity "Đại Thiên Thần" -> organization_faction
    assert normalize_library_type("Đại Thiên Thần", "entity") == "organization_faction"
    assert normalize_library_type("Hội Bạch Đường", "entity") == "organization_faction"

    # 7. entity generic unknown không auto-map bừa
    assert normalize_library_type("đây đã", "entity") == "entity"
    assert normalize_library_type("đại địa", "entity") == "entity"

def test_is_v2_type():
    assert is_v2_type("character") is True
    assert is_v2_type("crystal_core") is True
    assert is_v2_type("ability_skill") is True
    assert is_v2_type("entity") is False
    assert is_v2_type("ability") is False
    assert is_v2_type("") is False
    assert is_v2_type(None) is False

def test_build_type_normalization_plan():
    rows = [
        {"id": "1", "name": "Tinh thể zombie", "type": "item"},
        {"id": "2", "name": "Băng Độc", "type": "ability"},
        {"id": "3", "name": "Hàn Phong", "type": "character"}
    ]
    plan = build_type_normalization_plan(rows)
    assert len(plan) == 3
    
    assert plan[0]["new_type"] == "crystal_core"
    assert plan[0]["needs_normalization"] is True
    assert plan[0]["rule_applied"] == "item -> crystal_core"

    assert plan[1]["new_type"] == "ability_skill"
    assert plan[1]["needs_normalization"] is True
    assert plan[1]["rule_applied"] == "ability -> ability_skill"

    assert plan[2]["new_type"] == "character"
    assert plan[2]["needs_normalization"] is False
    assert plan[2]["rule_applied"] == "unchanged"

def test_dry_run_no_database_write(monkeypatch):
    # Mock Supabase to check that no updates are performed during dry-run
    import backend.scripts.normalize_provisional_library_types as normalizer

    called_update = False
    
    class MockExecuteResult:
        def __init__(self, data):
            self.data = data

    class MockQuery:
        def __init__(self, data=None):
            self.data = data or []
            self.filters = []

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
                {"id": "rec1", "name": "Tinh thể zombie", "type": "item", "source": "test", "quality_class": "high_confidence"},
                {"id": "rec2", "name": "Băng Độc", "type": "ability", "source": "test", "quality_class": "high_confidence"}
            ]
            return MockQuery(mock_data)

    monkeypatch.setattr(normalizer, "supabase", MockSupabaseClient())

    # Run script with default --dry-run
    sys.argv = ["normalize_provisional_library_types.py"]
    try:
        normalizer.main()
    except SystemExit as e:
        assert e.code == 0

    assert not called_update, "Database was mutated during dry-run!"

def test_no_llm_no_embedding_codebase():
    # 9. Không LLM.
    # 10. Không embedding.
    target_files = [
        "backend/rag/provisional_library_type_normalizer.py",
        "backend/scripts/audit_provisional_library_types.py",
        "backend/scripts/normalize_provisional_library_types.py"
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
