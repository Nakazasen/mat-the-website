import os
import sys
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

CRON_TOKEN = "test_cron_token_12345"


@pytest.fixture(autouse=True)
def setup_env():
    # Store original environment values
    orig_token = os.environ.get("ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN")
    
    # Set the test token
    os.environ["ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN"] = CRON_TOKEN
    yield
    
    # Restore original environment values
    if orig_token is not None:
        os.environ["ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN"] = orig_token
    elif "ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN"]


def test_cron_missing_env_token():
    # Temporarily remove env token
    if "ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN" in os.environ:
        del os.environ["ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN"]
        
    headers = {"X-Oracle-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post("/oracle/admin/run-feedback-policy-pipeline", json={}, headers=headers)
    assert response.status_code == 503
    assert "not configured on the server" in response.json()["detail"].lower()


def test_cron_missing_request_header():
    response = client.post("/oracle/admin/run-feedback-policy-pipeline", json={})
    assert response.status_code == 403
    assert "invalid pipeline cron token" in response.json()["detail"].lower()


def test_cron_invalid_request_header():
    headers = {"X-Oracle-Pipeline-Cron-Token": "wrong_cron_token"}
    response = client.post("/oracle/admin/run-feedback-policy-pipeline", json={}, headers=headers)
    assert response.status_code == 403
    assert "invalid pipeline cron token" in response.json()["detail"].lower()


@patch("backend.scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
@patch("scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
def test_cron_authorized_dry_run(mock_run_scripts, mock_run_backend):
    # Setup mock return value
    mock_report = {
        "feedback_rows_read": 10,
        "summary_rows_built": 5,
        "summary_rows_written": 5,
        "patches_built": 2,
        "patches_written": 2,
        "cache_rows_deleted": 1,
        "dry_run": True
    }
    mock_run_backend.return_value = mock_report
    mock_run_scripts.return_value = mock_report

    headers = {"X-Oracle-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post(
        "/oracle/admin/run-feedback-policy-pipeline",
        json={"dry_run": True, "clear_cache": True, "limit": 1000},
        headers=headers
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["ok"] is True
    assert res_json["dry_run"] is True
    assert res_json["report"]["feedback_rows_read"] == 10
    
    # Assert called with correct parameters
    called_mock = mock_run_backend if mock_run_backend.called else mock_run_scripts
    called_mock.assert_called_once()
    kwargs = called_mock.call_args[1]
    assert kwargs["dry_run"] is True
    assert kwargs["limit"] == 1000
    assert kwargs["clear_cache"] is True


@patch("backend.scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
@patch("scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
def test_cron_authorized_write_mode(mock_run_scripts, mock_run_backend):
    mock_report = {
        "feedback_rows_read": 5,
        "summary_rows_built": 2,
        "summary_rows_written": 2,
        "patches_built": 1,
        "patches_written": 1,
        "cache_rows_deleted": 0,
        "dry_run": False
    }
    mock_run_backend.return_value = mock_report
    mock_run_scripts.return_value = mock_report

    headers = {"X-Oracle-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post(
        "/oracle/admin/run-feedback-policy-pipeline",
        json={"dry_run": False, "clear_cache": False, "limit": 5000},
        headers=headers
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["ok"] is True
    assert res_json["dry_run"] is False
    assert res_json["report"]["summary_rows_written"] == 2
    
    called_mock = mock_run_backend if mock_run_backend.called else mock_run_scripts
    called_mock.assert_called_once()
    kwargs = called_mock.call_args[1]
    assert kwargs["dry_run"] is False
    assert kwargs["limit"] == 5000
    assert kwargs["clear_cache"] is False


@patch("backend.scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
@patch("scripts.run_feedback_policy_pipeline.run_feedback_policy_pipeline")
def test_cron_limit_capping(mock_run_scripts, mock_run_backend):
    mock_report = {"dry_run": True}
    mock_run_backend.return_value = mock_report
    mock_run_scripts.return_value = mock_report

    headers = {"X-Oracle-Pipeline-Cron-Token": CRON_TOKEN}
    # Send a limit above the 20000 cap (e.g. 50000)
    response = client.post(
        "/oracle/admin/run-feedback-policy-pipeline",
        json={"dry_run": True, "limit": 50000},
        headers=headers
    )
    
    # The request is valid but FastAPI/Manual validation will cap/restrict it.
    # If using Field(..., le=20000), it will trigger a 422 validation error or manual capping.
    # Let's handle either a 422 Unprocessable Entity, or it succeeds and limits to 20000.
    # Since RunPipelineRequest defines Field(..., le=20000), it should raise 422.
    assert response.status_code == 422
    err_type = response.json()["detail"][0]["type"]
    assert "validation_error" in err_type or "value_error" in err_type or "less_than_equal" in err_type
