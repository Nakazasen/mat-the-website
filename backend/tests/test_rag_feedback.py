import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

try:
    from main import app
except ImportError:
    from backend.main import app

client = TestClient(app)


def patch_supabase():
    import sys
    
    # Force load modules to ensure they exist in sys.modules
    try:
        import main
    except ImportError:
        pass
    try:
        import backend.main
    except ImportError:
        pass
    try:
        import routes.ai_oracle
    except ImportError:
        pass
    try:
        import backend.routes.ai_oracle
    except ImportError:
        pass

    mock_supabase = MagicMock()
    patched = []
    
    targets = [
        "main.supabase",
        "backend.main.supabase",
        "routes.ai_oracle.supabase",
        "backend.routes.ai_oracle.supabase"
    ]
    
    for target in targets:
        try:
            p = patch(target, mock_supabase)
            p.start()
            patched.append(p)
        except Exception:
            pass

    return mock_supabase, patched


def stop_patches(patched):
    for p in patched:
        try:
            p.stop()
        except Exception:
            pass


def test_migration_files_exist():
    migration_path1 = os.path.join("backend", "migrations", "create_rag_feedback_and_corrections.sql")
    assert os.path.exists(migration_path1), "Migration file must exist"
    with open(migration_path1, "r", encoding="utf-8") as f:
        content = f.read()
    assert "rag_feedback" in content
    assert "rag_corrections" in content

    migration_path2 = os.path.join("backend", "migrations", "add_rag_feedback_review_fields.sql")
    assert os.path.exists(migration_path2), "Migration file 2 must exist"
    with open(migration_path2, "r", encoding="utf-8") as f:
        content = f.read()
    assert "reviewer_note" in content
    assert "reviewed_at" in content


def test_submit_valid_feedback():
    mock_supabase, patched = patch_supabase()

    mock_resp = MagicMock()
    mock_resp.data = [{"id": "test-uuid-1234"}]
    mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_resp

    payload = {
        "question": "Hàn Phong là ai?",
        "answer": "Hàn Phong là nhân vật chính.",
        "source": "rag_answer_preview",
        "citations": [{"chapter": 1}],
        "chapter_progress": 10,
        "feedback_type": "wrong",
        "user_comment": "Thông tin chưa đúng lắm",
        "suggested_correction": "Sửa lại thành..."
    }

    try:
        response = client.post("/oracle/feedback", json=payload)
        if response.status_code not in [200, 201]:
            print("ERROR RESPONSE:", response.text)
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["ok"] is True
        assert data["feedback_id"] == "test-uuid-1234"
        assert data["status"] == "pending"

        mock_supabase.table.assert_called_with("rag_feedback")
        called_args = mock_supabase.table.return_value.insert.call_args[0][0]
        assert called_args["status"] == "pending"
        assert called_args["feedback_type"] == "wrong"
    finally:
        stop_patches(patched)


def test_submit_invalid_feedback_type():
    payload = {
        "question": "Hàn Phong là ai?",
        "feedback_type": "very_wrong",  # Invalid type
    }
    response = client.post("/oracle/feedback", json=payload)
    assert response.status_code == 422


def test_submit_too_long_fields():
    payload = {
        "question": "a" * 1001,  # Max 1000
        "feedback_type": "wrong",
    }
    response = client.post("/oracle/feedback", json=payload)
    assert response.status_code == 422

    payload2 = {
        "question": "Valid?",
        "feedback_type": "wrong",
        "answer": "b" * 8001,  # Max 8000
    }
    response2 = client.post("/oracle/feedback", json=payload2)
    assert response2.status_code == 422


def test_submit_citations_not_list():
    payload = {
        "question": "Hàn Phong là ai?",
        "feedback_type": "wrong",
        "citations": "not-a-list"  # Invalid
    }
    response = client.post("/oracle/feedback", json=payload)
    assert response.status_code == 422


def test_admin_pending_no_token():
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]

    response = client.get("/oracle/feedback/pending")
    assert response.status_code == 403


def test_admin_pending_wrong_token():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "wrong-token"}
    response = client.get("/oracle/feedback/pending", headers=headers)
    assert response.status_code == 403


def test_admin_pending_correct_token():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "super-secret-admin-token"}

    mock_supabase, patched = patch_supabase()

    mock_resp = MagicMock()
    mock_resp.data = [
        {"id": "uuid-1", "question": "Q1", "status": "pending"},
        {"id": "uuid-2", "question": "Q2", "status": "pending"},
    ]

    table_mock = mock_supabase.table
    select_mock = table_mock.return_value.select
    eq_mock = select_mock.return_value.eq
    order_mock = eq_mock.return_value.order
    limit_mock = order_mock.return_value.limit
    limit_mock.return_value.execute.return_value = mock_resp

    try:
        response = client.get("/oracle/feedback/pending", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["question"] == "Q1"
        assert data[1]["question"] == "Q2"

        table_mock.assert_called_with("rag_feedback")
        eq_mock.assert_called_with("status", "pending")
    finally:
        stop_patches(patched)
        if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
            del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]


def test_patch_feedback_no_token():
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]
    response = client.patch("/oracle/feedback/test-uuid", json={"status": "resolved"})
    assert response.status_code == 403


def test_patch_feedback_wrong_token():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "wrong-token"}
    response = client.patch("/oracle/feedback/test-uuid", json={"status": "resolved"}, headers=headers)
    assert response.status_code == 403
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]


def test_patch_feedback_invalid_status():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "super-secret-admin-token"}
    response = client.patch("/oracle/feedback/test-uuid", json={"status": "pending"}, headers=headers)
    assert response.status_code == 422
    response2 = client.patch("/oracle/feedback/test-uuid", json={"status": "bad-status"}, headers=headers)
    assert response2.status_code == 422
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]


def test_patch_feedback_too_long_note():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "super-secret-admin-token"}
    payload = {
        "status": "resolved",
        "reviewer_note": "a" * 2001  # Max 2000
    }
    response = client.patch("/oracle/feedback/test-uuid", json=payload, headers=headers)
    assert response.status_code == 422
    if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]


def test_patch_feedback_not_found():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "super-secret-admin-token"}

    mock_supabase, patched = patch_supabase()
    mock_resp = MagicMock()
    mock_resp.data = []
    # Chain: mock_supabase.table().select().eq().execute()
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_resp

    try:
        response = client.patch("/oracle/feedback/test-uuid", json={"status": "resolved"}, headers=headers)
        assert response.status_code == 404
        assert "Feedback not found" in response.json()["detail"]
    finally:
        stop_patches(patched)
        if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
            del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]


def test_patch_feedback_success():
    os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "super-secret-admin-token"
    headers = {"X-Oracle-Feedback-Admin-Token": "super-secret-admin-token"}

    mock_supabase, patched = patch_supabase()

    mock_select_resp = MagicMock()
    mock_select_resp.data = [{"id": "test-uuid"}]
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_select_resp

    mock_update_resp = MagicMock()
    mock_update_resp.data = [{"id": "test-uuid", "status": "resolved"}]
    mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_update_resp

    payload = {
        "status": "resolved",
        "reviewer_note": "Smoke test resolved note"
    }

    try:
        response = client.patch("/oracle/feedback/test-uuid", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["feedback_id"] == "test-uuid"
        assert data["status"] == "resolved"

        mock_supabase.table.assert_called_with("rag_feedback")
    finally:
        stop_patches(patched)
        if "ORACLE_FEEDBACK_ADMIN_TOKEN" in os.environ:
            del os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"]
