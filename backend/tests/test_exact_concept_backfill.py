import json
import os
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.rag.library_taxonomy_v2 import classify_term_v2
from backend.rag.exact_concept_backfill import build_backfill_candidate, generate_stable_id
from backend.scripts.import_exact_concept_backfills import build_db_payload

def test_taxonomy_classification():
    # 1. Tinh thạch khai phá phân loại crystal_core
    assert classify_term_v2("Tinh thạch khai phá") == "crystal_core"
    
    # 2. Súng Diệt Quỷ phân loại weapon
    assert classify_term_v2("Súng Diệt Quỷ") == "weapon"
    
    # 3. Băng Độc phân loại ability_skill
    assert classify_term_v2("Băng Độc") == "ability_skill"

def test_backfill_candidate_creation():
    # Tinh thể zombie có evidence phrase thì tạo candidate crystal_core
    evidence = [
        {
            "chapter_number": 9,
            "chapter_title": "Thoát đi",
            "chunk_index": 1,
            "content_hash": "d07388168bab26b6ff2d2c8a64887988f8c75c23bbbb45768580fd9a825acb0f",
            "preview": "Hai bản sách kỹ năng, một thẻ vật phẩm, một tinh thạch exp"
        }
    ]
    candidate = build_backfill_candidate("Tinh thể zombie", "crystal_core", evidence)
    
    assert candidate["name"] == "Tinh thể zombie"
    assert candidate["type"] == "crystal_core"
    assert len(candidate["evidence"]) == 1
    assert candidate["confidence"] == 0.3  # min(1.0, 0.1 + 0.2 * 1) = 0.3
    assert candidate["quality_class"] == "medium_confidence"
    assert candidate["source"] == "exact_concept_backfill_v1"
    assert "Tinh thể zombie" in candidate["summary"]
    assert candidate["chapter_numbers"] == [9]
    assert candidate["first_chapter"] == 9
    assert candidate["last_chapter"] == 9

def test_db_payload_structure():
    candidate = {
        "id": "af4b58bae3bccafeb454f5c7b6a16e2a",
        "name": "Tinh thể zombie",
        "normalized_name": "Tinh thể zombie",
        "type": "crystal_core",
        "summary": "Khái niệm 'Tinh thể zombie' xuất hiện trong truyện.",
        "evidence": [],
        "confidence": 0.3,
        "quality_class": "medium_confidence",
        "status": "provisional",
        "source": "exact_concept_backfill_v1",
        "feedback_score": 0,
        "needs_review": False,
        "chapter_numbers": [9],
        "first_chapter": 9,
        "last_chapter": 9
    }
    payload = build_db_payload(candidate)
    
    assert payload["id"] == "af4b58bae3bccafeb454f5c7b6a16e2a"
    assert payload["name"] == "Tinh thể zombie"
    assert payload["type"] == "crystal_core"
    assert payload["source"] == "exact_concept_backfill_v1"

def test_no_llm_no_embedding_no_db_on_dryrun(monkeypatch):
    # Verify no LLM or embedding imports/calls
    files_to_check = [
        "backend/rag/exact_concept_backfill.py",
        "backend/scripts/audit_missing_exact_concepts.py",
        "backend/scripts/build_exact_concept_backfills.py",
        "backend/scripts/import_exact_concept_backfills.py"
    ]
    for fn in files_to_check:
        full_path = os.path.join(str(REPO_ROOT), fn.replace("/", os.sep))
        with open(full_path, "r", encoding="utf-8") as f:
            code = f.read()
            assert "import openai" not in code.lower()
            assert "import anthropic" not in code.lower()
            assert "import cohere" not in code.lower()
            assert "openai.client" not in code.lower()


    # Verify dry-run doesn't write to DB (checked via script CLI dry-run test)
    # We can mock supabase to guarantee no write calls are made
    import backend.scripts.import_exact_concept_backfills as importer
    
    called_upsert = False
    class MockTable:
        def upsert(self, *args, **kwargs):
            nonlocal called_upsert
            called_upsert = True
            return self
        def execute(self, *args, **kwargs):
            return self

    class MockClient:
        def table(self, table_name):
            assert table_name == "provisional_library"
            return MockTable()

    monkeypatch.setattr(importer, "supabase", MockClient())
    
    # Run import script in dry-run mode
    # Should not call upsert
    sys.argv = ["import_exact_concept_backfills.py", "--dry-run"]
    try:
        importer.main()
    except SystemExit as e:
        assert e.code == 0
        
    assert not called_upsert, "Upsert was called during dry-run!"
