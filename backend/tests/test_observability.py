import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure correct path resolution
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.scripts.run_feedback_policy_pipeline import run_feedback_policy_pipeline

class MockSupabase:
    def __init__(self):
        self.inserted_runs = []
        self.upserted_summaries = []
        self.inserted_patches = []
        self.deleted_cache = []

    def table(self, table_name):
        return MockQueryBuilder(self, table_name)

class MockQueryBuilder:
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.filters = {}

    def select(self, fields=None, options=None):
        self.filters["select"] = fields
        return self

    def eq(self, field, value):
        self.filters[f"eq_{field}"] = value
        return self

    def in_(self, field, values):
        self.filters[f"in_{field}"] = values
        return self

    def gte(self, field, value):
        self.filters[f"gte_{field}"] = value
        return self

    def limit(self, value):
        self.filters["limit"] = value
        return self

    def upsert(self, data):
        self.client.upserted_summaries.extend(data)
        return self

    def insert(self, data):
        if self.table_name == "feedback_policy_pipeline_runs":
            self.client.inserted_runs.append(data)
        elif self.table_name == "provisional_library_effective_patches":
            self.client.inserted_patches.extend(data)
        return self

    def delete(self):
        self.filters["delete"] = True
        return self

    def execute(self):
        class MockResponse:
            def __init__(self, data):
                self.data = data
        
        # Default mock data returned
        data = []
        if self.table_name == "provisional_library_feedback":
            data = [
                {
                    "id": "fb-123",
                    "provisional_id": "record-123",
                    "record_name": "Entity Name",
                    "feedback_type": "wrong_info",
                    "user_comment": "This is incorrect.",
                    "user_agent": "Mozilla",
                    "created_at": "2026-06-08T00:00:00Z"
                }
            ]
        elif self.table_name == "provisional_library":
            data = [
                {
                    "id": "record-123",
                    "name": "Entity Name",
                    "description": "Old description."
                }
            ]
        elif self.table_name == "provisional_library_effective_patches":
            data = []
        elif self.table_name == "oracle_cache":
            data = [
                {
                    "id": 1,
                    "response": "Entity Name is great."
                }
            ]
            
        return MockResponse(data)


@patch("backend.scripts.run_feedback_policy_pipeline.fetch_feedback_records")
@patch("backend.scripts.run_feedback_policy_pipeline.fetch_provisional_records")
def test_pipeline_observability_logging_success(mock_prov, mock_fb):
    client = MockSupabase()
    
    mock_fb.return_value = [
        {
            "id": "fb-1",
            "provisional_id": "prov-1",
            "record_name": "Test Target",
            "feedback_type": "wrong_info",
            "user_comment": "Incorrect summary",
            "user_agent": "Agent1",
            "created_at": "2026-06-08T00:00:00Z"
        }
    ]
    mock_prov.return_value = {
        "prov-1": {
            "id": "prov-1",
            "name": "Test Target"
        }
    }

    report = run_feedback_policy_pipeline(
        supabase_client=client,
        dry_run=True,
        limit=10,
        clear_cache=True,
        log_run=True,
        trigger_source="manual"
    )

    assert report["feedback_rows_read"] == 1
    assert len(client.inserted_runs) == 1
    
    run_log = client.inserted_runs[0]
    assert run_log["ok"] is True
    assert run_log["trigger_source"] == "manual"
    assert run_log["dry_run"] is True
    assert run_log["feedback_rows_read"] == 1
    assert run_log["errors"] == []


@patch("backend.scripts.run_feedback_policy_pipeline.fetch_feedback_records")
def test_pipeline_observability_logging_failure(mock_fb):
    client = MockSupabase()
    # Trigger an exception during pipeline execution
    mock_fb.side_effect = Exception("Database connection failure")

    with pytest.raises(RuntimeError) as exc_info:
        run_feedback_policy_pipeline(
            supabase_client=client,
            dry_run=False,
            limit=50,
            clear_cache=False,
            log_run=True,
            trigger_source="github_actions"
        )

    assert "Pipeline finished with errors" in str(exc_info.value)
    assert len(client.inserted_runs) == 1
    
    run_log = client.inserted_runs[0]
    assert run_log["ok"] is False
    assert run_log["trigger_source"] == "github_actions"
    assert run_log["dry_run"] is False
    assert "Database connection failure" in run_log["errors"][0]
