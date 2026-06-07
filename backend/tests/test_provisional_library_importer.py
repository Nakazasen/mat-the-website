import pytest
import json
from typing import Dict, Any

from backend.rag.provisional_library_importer import (
    load_ranked_library,
    filter_importable_records,
    build_db_payload,
    upsert_provisional_records,
    summarize_import
)

def test_filter_importable_records():
    # 1. filter chỉ lấy high/medium.
    # 2. weak/discard bị loại.
    records = [
        {"name": "A", "quality_class": "high_confidence"},
        {"name": "B", "quality_class": "medium_confidence"},
        {"name": "C", "quality_class": "weak_evidence"},
        {"name": "D", "quality_class": "discard_candidate"}
    ]
    filtered = filter_importable_records(records)
    assert len(filtered) == 2
    assert filtered[0]["name"] == "A"
    assert filtered[1]["name"] == "B"

def test_build_db_payload():
    # 3. build_db_payload giữ evidence.
    # 4. chapter_numbers/first/last đúng.
    record = {
        "id": "abc123hash",
        "name": "Tinh thể zombie",
        "type": "item",
        "summary": "Tinh thể thu được từ zombie.",
        "evidence": [
            {"chapter_number": 8, "chapter_title": "Chương 8", "preview": "..." },
            {"chapter_number": 14, "chapter_title": "Chương 14", "preview": "..." },
            {"chapter_number": 8, "chapter_title": "Chương 8", "preview": "duplicate" }
        ],
        "confidence": 0.5,
        "quality_class": "medium_confidence"
    }
    payload = build_db_payload(record)
    
    assert payload["id"] == "abc123hash"
    assert payload["name"] == "Tinh thể zombie"
    assert payload["normalized_name"] == "Tinh thể zombie"
    assert payload["type"] == "item"
    assert len(payload["evidence"]) == 3
    assert payload["chapter_numbers"] == [8, 14]
    assert payload["first_chapter"] == 8
    assert payload["last_chapter"] == 14
    assert payload["confidence"] == 0.5
    assert payload["quality_class"] == "medium_confidence"

def test_upsert_provisional_records_dry_run():
    # 5. dry-run không gọi upsert.
    mock_supabase = None
    records = [{"id": "id1", "name": "Hàn Phong", "quality_class": "high_confidence"}]
    
    summary = upsert_provisional_records(mock_supabase, records, dry_run=True)
    assert summary["processed"] == 1
    assert summary["upserted"] == 1
    assert summary["failed"] == 0

class MockTable:
    def __init__(self, table_name):
        self.table_name = table_name
        self.upsert_called_with = None
        
    def upsert(self, payload):
        self.upsert_called_with = payload
        return self
        
    def execute(self):
        return self

class MockSupabase:
    def __init__(self):
        self.tables = {}
        
    def table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = MockTable(table_name)
        return self.tables[table_name]

def test_upsert_provisional_records_write():
    # 6. write mode gọi upsert đúng table provisional_library.
    mock_supabase = MockSupabase()
    records = [{
        "id": "id1",
        "name": "Hàn Phong",
        "quality_class": "high_confidence",
        "evidence": [{"chapter_number": 1}]
    }]
    
    summary = upsert_provisional_records(mock_supabase, records, dry_run=False)
    assert summary["processed"] == 1
    assert summary["upserted"] == 1
    assert summary["failed"] == 0
    
    assert "provisional_library" in mock_supabase.tables
    upserted_payloads = mock_supabase.tables["provisional_library"].upsert_called_with
    assert len(upserted_payloads) == 1
    assert upserted_payloads[0]["id"] == "id1"

def test_strict_constraints():
    # 7. không có write path wiki_entries.
    # 8. JSON serializable.
    import inspect
    import backend.rag.provisional_library_importer as pli
    
    source_code = inspect.getsource(pli)
    assert "wiki_entries" not in source_code
    
    record = {
        "id": "id1",
        "name": "Hàn Phong",
        "type": "entity",
        "summary": "Nhân vật chính.",
        "evidence": [{"chapter_number": 1}],
        "confidence": 0.7,
        "quality_class": "high_confidence"
    }
    payload = build_db_payload(record)
    serialized = json.dumps(payload)
    assert serialized is not None
