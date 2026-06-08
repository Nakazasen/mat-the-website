import os
import sys
import pytest
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.rag.oracle_cache_invalidation import (
    normalize_cache_term,
    build_cache_invalidation_terms,
    find_oracle_cache_rows_for_terms,
    clear_oracle_cache_for_terms
)

class MockExecuteResult:
    def __init__(self, data):
        self.data = data

class MockQuery:
    def __init__(self, data, delete_callback=None):
        self.data = data
        self.delete_callback = delete_callback
        self.filters = []

    def select(self, *args, **kwargs):
        return self

    def or_(self, filter_str):
        self.filters.append(("or", filter_str))
        return self

    def eq(self, field, value):
        self.filters.append(("eq", field, value))
        return self

    def limit(self, limit_val):
        return self

    def delete(self):
        if self.delete_callback:
            self.delete_callback()
        return self

    def upsert(self, payloads):
        return self

    def execute(self):
        return MockExecuteResult(self.data)

class MockSupabaseClient:
    def __init__(self, select_data=None, delete_callback=None):
        self.select_data = select_data or []
        self.delete_callback = delete_callback
        self.queries_created = []

    def table(self, name):
        if name == "provisional_library":
            return MockQuery([])
        assert name == "oracle_cache"
        query = MockQuery(self.select_data, self.delete_callback)
        self.queries_created.append(query)
        return query

def test_normalize_cache_term():
    assert normalize_cache_term("  Tinh  thể   zombie  ") == "Tinh thể zombie"
    assert normalize_cache_term("") == ""
    assert normalize_cache_term(None) == ""

def test_build_cache_invalidation_terms():
    # Mix of strings, dicts, duplicates, empty strings
    raw = [
        "Tinh thể zombie",
        {"name": "Tinh thạch khai phá"},
        " tinh thể zombie ",  # duplicate normalized case-insensitive
        "",
        {"name": None},
        "Súng Diệt Quỷ"
    ]
    terms = build_cache_invalidation_terms(raw)
    assert terms == ["Tinh thể zombie", "Tinh thạch khai phá", "Súng Diệt Quỷ"]

def test_empty_terms_no_delete():
    # 1. Empty terms => skip, no delete
    client = MockSupabaseClient()
    report = clear_oracle_cache_for_terms(client, terms=[], dry_run=False)
    assert report["skipped_reason"] == "No terms or question hashes provided"
    assert report["matched_rows"] == 0
    assert report["deleted_rows"] == 0
    assert len(client.queries_created) == 0

def test_dry_run_returns_matched_rows_no_delete():
    # 2. Dry-run returns matched rows, no delete
    mock_rows = [
        {"question_hash": "hash1", "chapter_cap": 9, "response": "Đây là Tinh thể zombie"},
        {"question_hash": "hash2", "chapter_cap": 9, "response": "Có chứa Tinh thạch khai phá"}
    ]
    
    delete_called = False
    def on_delete():
        nonlocal delete_called
        delete_called = True

    client = MockSupabaseClient(select_data=mock_rows, delete_callback=on_delete)
    terms = ["Tinh thể zombie", "Tinh thạch khai phá"]
    
    report = clear_oracle_cache_for_terms(client, terms=terms, dry_run=True)
    assert report["dry_run"] is True
    assert report["matched_rows"] == 2
    assert report["deleted_rows"] == 0
    assert not delete_called

def test_write_deletes_only_matched_rows():
    # 3. Write deletes only matched rows
    mock_rows = [
        {"question_hash": "hash1", "chapter_cap": 9, "response": "Đây là Tinh thể zombie"},
        {"question_hash": "hash2", "chapter_cap": 12, "response": "Có chứa Tinh thạch khai phá"}
    ]
    
    deleted_queries = []
    class RecordingQuery(MockQuery):
        def delete(self):
            return self
        def eq(self, field, value):
            self.filters.append((field, value))
            return self
        def execute(self):
            deleted_queries.append(self.filters)
            return MockExecuteResult([])

    class RecordingSupabaseClient(MockSupabaseClient):
        def table(self, name):
            if len(self.queries_created) == 0:
                # First call is select
                q = MockQuery(mock_rows)
            else:
                # Subsequent calls are deletes
                q = RecordingQuery([])
            self.queries_created.append(q)
            return q

    client = RecordingSupabaseClient()
    terms = ["Tinh thể zombie", "Tinh thạch khai phá"]
    
    report = clear_oracle_cache_for_terms(client, terms=terms, dry_run=False)
    assert report["dry_run"] is False
    assert report["matched_rows"] == 2
    assert report["deleted_rows"] == 2
    
    # Verify exact delete calls matching question_hash & chapter_cap
    assert len(deleted_queries) == 2
    # First delete
    assert ("question_hash", "hash1") in deleted_queries[0]
    assert ("chapter_cap", 9) in deleted_queries[0]
    # Second delete
    assert ("question_hash", "hash2") in deleted_queries[1]
    assert ("chapter_cap", 12) in deleted_queries[1]

def test_does_not_wipe_cache_when_target_name_empty():
    # 4. Does not wipe cache when target_name empty or spaces
    client = MockSupabaseClient()
    terms = build_cache_invalidation_terms(["   ", ""])
    assert len(terms) == 0
    report = clear_oracle_cache_for_terms(client, terms=terms, dry_run=False)
    assert report["matched_rows"] == 0
    assert report["deleted_rows"] == 0
    assert len(client.queries_created) == 0

def test_import_exact_backfill_calls_invalidation_flag(monkeypatch):
    # 6. Import exact backfill calls invalidation only when --clear-cache
    import backend.scripts.import_exact_concept_backfills as backfill_importer
    
    invalidation_calls = []
    def dummy_clear_cache(supabase, terms, dry_run, **kwargs):
        invalidation_calls.append((terms, dry_run))
        return {
            "dry_run": dry_run,
            "terms": terms,
            "matched_rows": 5,
            "deleted_rows": 0 if dry_run else 5,
            "skipped_reason": None
        }

    monkeypatch.setattr(backfill_importer, "supabase", MockSupabaseClient())
    # Mock the imported function inside the source module namespace
    monkeypatch.setattr(
        "backend.rag.oracle_cache_invalidation.clear_oracle_cache_for_terms",
        dummy_clear_cache
    )
    
    # Run with --clear-cache
    sys.argv = ["import_exact_concept_backfills.py", "--write", "--clear-cache", "--cache-dry-run"]
    try:
        backfill_importer.main()
    except SystemExit as e:
        assert e.code == 0
        
    assert len(invalidation_calls) == 1
    terms_passed, is_dry = invalidation_calls[0]
    assert is_dry is True
    assert "Tinh thể zombie" in terms_passed

    # Reset calls and run WITHOUT --clear-cache
    invalidation_calls.clear()
    sys.argv = ["import_exact_concept_backfills.py", "--write"]
    try:
        backfill_importer.main()
    except SystemExit as e:
        assert e.code == 0
    assert len(invalidation_calls) == 0

def test_import_v2_candidates_calls_invalidation_flag(monkeypatch):
    # Test integration in V2 candidate importer
    import backend.scripts.import_provisional_library_v2_candidates as v2_importer
    
    invalidation_calls = []
    def dummy_clear_cache(supabase, terms, dry_run, **kwargs):
        invalidation_calls.append((terms, dry_run))
        return {
            "dry_run": dry_run,
            "terms": terms,
            "matched_rows": 10,
            "deleted_rows": 0 if dry_run else 10,
            "skipped_reason": None
        }

    monkeypatch.setattr(v2_importer, "supabase", MockSupabaseClient())
    monkeypatch.setattr(
        "backend.rag.oracle_cache_invalidation.clear_oracle_cache_for_terms",
        dummy_clear_cache
    )
    
    # Run with --clear-cache and cache limit of 2 terms
    sys.argv = [
        "import_provisional_library_v2_candidates.py",
        "--write",
        "--clear-cache",
        "--cache-dry-run",
        "--cache-limit-terms", "2"
    ]
    try:
        v2_importer.main()
    except SystemExit as e:
        assert e.code == 0
        
    assert len(invalidation_calls) == 1
    terms_passed, is_dry = invalidation_calls[0]
    assert is_dry is True
    # Should be truncated to 2 elements since we set --cache-limit-terms 2
    assert len(terms_passed) == 2

    # Reset calls and run WITHOUT --clear-cache
    invalidation_calls.clear()
    sys.argv = ["import_provisional_library_v2_candidates.py", "--write"]
    try:
        v2_importer.main()
    except SystemExit as e:
        assert e.code == 0
    assert len(invalidation_calls) == 0

def test_no_llm_no_embedding_codebase():
    # 7. Không LLM.
    # 8. Không embedding.
    target_files = [
        "backend/rag/oracle_cache_invalidation.py",
        "backend/scripts/clear_oracle_cache_for_concepts.py",
        "backend/scripts/import_exact_concept_backfills.py",
        "backend/scripts/import_provisional_library_v2_candidates.py"
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
