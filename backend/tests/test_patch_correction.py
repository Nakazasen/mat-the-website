import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add current workspace to path
sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from main import app
except ImportError:
    from backend.main import app

from fastapi.testclient import TestClient

client = TestClient(app)

# Mock admin token
ADMIN_TOKEN = "test_admin_token_123"

@pytest.fixture(autouse=True)
def setup_env():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = ADMIN_TOKEN
    yield
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]

def test_patch_without_token():
    response = client.patch("/oracle/corrections/some-uuid", json={
        "status": "accepted",
        "reviewer_note": "Approved"
    })
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()

def test_patch_with_invalid_token():
    headers = {"X-Oracle-Feedback-Admin-Token": "wrong_token"}
    response = client.patch("/oracle/corrections/some-uuid", json={
        "status": "accepted",
        "reviewer_note": "Approved"
    }, headers=headers)
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()

@patch("main.supabase", create=True)
@patch("backend.main.supabase", create=True)
def test_patch_success_only_status_and_note(mock_supabase_backend, mock_supabase_main):
    # Setup mocks for both possible import paths
    for mock_supabase in [mock_supabase_backend, mock_supabase_main]:
        mock_select = MagicMock()
        mock_select.execute.return_value.data = [{"id": "uuid-123", "correction_type": "wiki_update"}]
        
        mock_update = MagicMock()
        mock_update.execute.return_value.data = [{"id": "uuid-123", "status": "approved"}]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_select
        mock_supabase.table.return_value.update.return_value.eq.return_value = mock_update

    headers = {"X-Oracle-Feedback-Admin-Token": ADMIN_TOKEN}
    response = client.patch("/oracle/corrections/uuid-123", json={
        "status": "accepted",
        "reviewer_note": "Valid reviewer note"
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["correction_id"] == "uuid-123"
    assert response.json()["status"] == "approved"

    # Verify update arguments
    active_mock = mock_supabase_main if mock_supabase_main.table.called else mock_supabase_backend
    active_mock.table.assert_any_call("rag_corrections")
    update_call = active_mock.table.return_value.update.call_args[0][0]
    assert update_call["status"] == "approved"
    assert update_call["reviewer_note"] == "Valid reviewer note"
    assert "proposed_content" not in update_call

@patch("main.supabase", create=True)
@patch("backend.main.supabase", create=True)
def test_patch_success_with_proposed_content(mock_supabase_backend, mock_supabase_main):
    for mock_supabase in [mock_supabase_backend, mock_supabase_main]:
        mock_select = MagicMock()
        mock_select.execute.return_value.data = [{"id": "uuid-123", "correction_type": "entity_profile"}]
        
        mock_update = MagicMock()
        mock_update.execute.return_value.data = [{"id": "uuid-123", "status": "approved"}]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_select
        mock_supabase.table.return_value.update.return_value.eq.return_value = mock_update

    proposed_json = json.dumps({"summary": "Test Summary", "content": "Test Content"})

    headers = {"X-Oracle-Feedback-Admin-Token": ADMIN_TOKEN}
    response = client.patch("/oracle/corrections/uuid-123", json={
        "status": "accepted",
        "reviewer_note": "wiki candidate edited",
        "proposed_content": proposed_json
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["ok"] is True

    active_mock = mock_supabase_main if mock_supabase_main.table.called else mock_supabase_backend
    update_call = active_mock.table.return_value.update.call_args[0][0]
    assert update_call["proposed_content"] == proposed_json

@patch("main.supabase", create=True)
@patch("backend.main.supabase", create=True)
def test_patch_reject_proposed_content_for_non_entity_profile(mock_supabase_backend, mock_supabase_main):
    for mock_supabase in [mock_supabase_backend, mock_supabase_main]:
        mock_select = MagicMock()
        # non-entity_profile type (e.g. wiki_update)
        mock_select.execute.return_value.data = [{"id": "uuid-123", "correction_type": "wiki_update"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_select

    proposed_json = json.dumps({"summary": "Test Summary"})

    headers = {"X-Oracle-Feedback-Admin-Token": ADMIN_TOKEN}
    response = client.patch("/oracle/corrections/uuid-123", json={
        "status": "accepted",
        "reviewer_note": "rejected update",
        "proposed_content": proposed_json
    }, headers=headers)

    assert response.status_code == 400
    assert "only entity_profile corrections" in response.json()["detail"].lower()

@patch("main.supabase", create=True)
@patch("backend.main.supabase", create=True)
def test_patch_reject_invalid_json_proposed_content(mock_supabase_backend, mock_supabase_main):
    for mock_supabase in [mock_supabase_backend, mock_supabase_main]:
        mock_select = MagicMock()
        mock_select.execute.return_value.data = [{"id": "uuid-123", "correction_type": "entity_profile"}]
        mock_supabase.table.return_value.select.return_value.eq.return_value = mock_select

    headers = {"X-Oracle-Feedback-Admin-Token": ADMIN_TOKEN}
    
    # 1. Invalid JSON string
    response = client.patch("/oracle/corrections/uuid-123", json={
        "status": "accepted",
        "proposed_content": "{invalid json"
    }, headers=headers)
    assert response.status_code == 400
    assert "must be a valid json string" in response.json()["detail"].lower()

    # 2. Valid JSON but not an object (e.g. integer or list)
    response = client.patch("/oracle/corrections/uuid-123", json={
        "status": "accepted",
        "proposed_content": "[1, 2, 3]"
    }, headers=headers)
    assert response.status_code == 400
    assert "must be a json object" in response.json()["detail"].lower()
