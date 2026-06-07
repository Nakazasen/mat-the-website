import pytest
from unittest.mock import MagicMock, patch
from backend.rag.effective_patch_engine import patch_dedupe_key
from backend.scripts.run_feedback_policy_pipeline import (
    write_summaries,
    write_patches,
    clear_selective_oracle_cache
)

class MockSupabase:
    def __init__(self, data=None):
        self.data = data or {}
        self.queries = []
        self.deleted = []

    def table(self, table_name):
        self.queries.append(table_name)
        return MockQueryBuilder(self, table_name)

class MockQueryBuilder:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.filters = {}

    def select(self, fields):
        self.filters["select"] = fields
        return self

    def eq(self, field, value):
        self.filters[f"eq_{field}"] = value
        return self

    def in_(self, field, values):
        self.filters[f"in_{field}"] = values
        return self

    def upsert(self, data, on_conflict=None):
        self.filters["upsert"] = data
        return self

    def insert(self, data):
        self.filters["insert"] = data
        return self

    def delete(self):
        self.filters["delete"] = True
        return self

    def execute(self):
        class MockResponse:
            def __init__(self, data):
                self.data = data
        
        # Mock responses
        if "delete" in self.filters:
            # Record what was deleted
            if f"in_id" in self.filters:
                deleted_ids = self.filters["in_id"]
                self.client.deleted.extend(deleted_ids)
                # Remove from client mock data
                if self.table_name in self.client.data:
                    self.client.data[self.table_name] = [
                        row for row in self.client.data[self.table_name]
                        if row.get("id") not in deleted_ids
                    ]
            return MockResponse([])

        if "upsert" in self.filters:
            upsert_data = self.filters["upsert"]
            if not isinstance(upsert_data, list):
                upsert_data = [upsert_data]
            return MockResponse(upsert_data)

        if "insert" in self.filters:
            insert_data = self.filters["insert"]
            if not isinstance(insert_data, list):
                insert_data = [insert_data]
            return MockResponse(insert_data)

        raw_data = self.client.data.get(self.table_name, [])
        return MockResponse(raw_data)


def test_dry_run_does_not_write():
    # Dry-run stats should just return the count without DB operations
    summaries = [{"provisional_id": "pid-1", "oracle_policy": "allow"}]
    res = write_summaries(summaries, dry_run=True)
    assert res["upserted"] == 1
    assert res["failed"] == 0

    patches = [{"target_id": "pid-1", "patch_type": "hide_record"}]
    res_patch = write_patches(patches, dry_run=True)
    assert res_patch["upserted"] == 1
    assert res_patch["failed"] == 0


def test_write_mode_executes_db_upsert():
    client = MockSupabase()
    summaries = [{"provisional_id": "pid-1", "oracle_policy": "allow"}]
    
    with patch("backend.scripts.run_feedback_policy_pipeline.supabase", client):
        res = write_summaries(summaries, dry_run=False)
        assert res["upserted"] == 1
        assert "provisional_library_feedback_summary" in client.queries


def test_patch_dedupe_key():
    payload1 = {
        "target_type": "provisional_record",
        "target_id": "pid-123",
        "target_name": "Hàn Phong ",
        "query_pattern": "Hàn Phong là ai?",
        "patch_type": "deprioritize_record"
    }
    payload2 = {
        "target_type": "provisional_record",
        "target_id": "pid-123",
        "target_name": "hàn phong",
        "query_pattern": " hàn phong là ai? ",
        "patch_type": "deprioritize_record"
    }
    assert patch_dedupe_key(payload1) == patch_dedupe_key(payload2)


def test_selective_cache_invalidation():
    mock_data = {
        "oracle_cache": [
            {"id": "cache-1", "response": "Hàn Phong là một đoàn trưởng dũng mãnh."},
            {"id": "cache-2", "response": "Chu Vấn thuộc quân đội căn cứ."},
            {"id": "cache-3", "response": "đệ Hàn Phong xuất hiện ở chương sau."}
        ]
    }
    client = MockSupabase(mock_data)
    
    with patch("backend.scripts.run_feedback_policy_pipeline.supabase", client):
        # Clear cache for Hàn Phong
        deleted = clear_selective_oracle_cache(["Hàn Phong"], dry_run=False)
        assert deleted == 2  # Match cache-1 and cache-3
        assert "cache-1" in client.deleted
        assert "cache-3" in client.deleted
        assert "cache-2" not in client.deleted


def test_idempotency_avoids_duplicate_patches():
    # If the patch dedupe key is already present in existing active patches,
    # the pipeline should not write it.
    from backend.scripts.run_feedback_policy_pipeline import fetch_existing_active_patches
    mock_data = {
        "provisional_library_effective_patches": [
            {
                "id": "existing-1",
                "target_type": "provisional_record",
                "target_id": "pid-1",
                "target_name": "Hàn Phong",
                "query_pattern": "Hàn Phong là ai?",
                "patch_type": "hide_record",
                "effective_status": "active"
            }
        ]
    }
    client = MockSupabase(mock_data)
    
    with patch("backend.scripts.run_feedback_policy_pipeline.supabase", client):
        existing = fetch_existing_active_patches()
        existing_keys = {patch_dedupe_key(p) for p in existing}
        
        new_payload = {
            "target_type": "provisional_record",
            "target_id": "pid-1",
            "target_name": "hàn phong",
            "query_pattern": "Hàn Phong là ai?",
            "patch_type": "hide_record"
        }
        
        # Verify it generates same key
        assert patch_dedupe_key(new_payload) in existing_keys
