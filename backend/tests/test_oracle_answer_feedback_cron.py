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

CRON_TOKEN = "test_oracle_cron_token_12345"


@pytest.fixture(autouse=True)
def setup_env():
    # Store original environment values
    orig_token = os.environ.get("ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN")
    
    # Set the test token
    os.environ["ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN"] = CRON_TOKEN
    yield
    
    # Restore original environment values
    if orig_token is not None:
        os.environ["ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN"] = orig_token
    elif "ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN" in os.environ:
        del os.environ["ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN"]


def test_cron_missing_env_token():
    # Temporarily remove env token
    if "ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN" in os.environ:
        del os.environ["ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN"]
        
    headers = {"X-Oracle-Answer-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post("/oracle/admin/run-oracle-answer-feedback-pipeline", json={}, headers=headers)
    assert response.status_code == 503
    assert "not configured on the server" in response.json()["detail"].lower()


def test_cron_missing_request_header():
    response = client.post("/oracle/admin/run-oracle-answer-feedback-pipeline", json={})
    assert response.status_code == 403
    assert "invalid oracle answer pipeline cron token" in response.json()["detail"].lower()


def test_cron_invalid_request_header():
    headers = {"X-Oracle-Answer-Pipeline-Cron-Token": "wrong_cron_token"}
    response = client.post("/oracle/admin/run-oracle-answer-feedback-pipeline", json={}, headers=headers)
    assert response.status_code == 403
    assert "invalid oracle answer pipeline cron token" in response.json()["detail"].lower()


@patch("backend.scripts.run_oracle_answer_feedback_pipeline.run_oracle_answer_feedback_pipeline")
@patch("scripts.run_oracle_answer_feedback_pipeline.run_oracle_answer_feedback_pipeline")
def test_cron_authorized_dry_run(mock_run_scripts, mock_run_backend):
    # Setup mock return value
    mock_report = {
        "feedback_rows_read": 12,
        "summary_rows_written": 3,
        "patches_written": 3,
        "cache_rows_deleted": 2,
        "dry_run": True,
        "ok": True,
        "errors": []
    }
    mock_run_backend.return_value = mock_report
    mock_run_scripts.return_value = mock_report

    headers = {"X-Oracle-Answer-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post(
        "/oracle/admin/run-oracle-answer-feedback-pipeline",
        json={"dry_run": True, "clear_cache": True, "limit": 1000},
        headers=headers
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["ok"] is True
    assert res_json["dry_run"] is True
    assert res_json["report"]["feedback_rows_read"] == 12
    
    # Assert token is not returned in the payload
    assert CRON_TOKEN not in str(res_json)
    
    # Assert called with correct parameters
    called_mock = mock_run_backend if mock_run_backend.called else mock_run_scripts
    called_mock.assert_called_once()
    kwargs = called_mock.call_args[1]
    assert kwargs["dry_run"] is True
    assert kwargs["limit"] == 1000
    assert kwargs["clear_cache"] is True


@patch("backend.scripts.run_oracle_answer_feedback_pipeline.run_oracle_answer_feedback_pipeline")
@patch("scripts.run_oracle_answer_feedback_pipeline.run_oracle_answer_feedback_pipeline")
def test_cron_authorized_write_mode(mock_run_scripts, mock_run_backend):
    mock_report = {
        "feedback_rows_read": 8,
        "summary_rows_written": 2,
        "patches_written": 2,
        "cache_rows_deleted": 0,
        "dry_run": False,
        "ok": True,
        "errors": []
    }
    mock_run_backend.return_value = mock_report
    mock_run_scripts.return_value = mock_report

    headers = {"X-Oracle-Answer-Pipeline-Cron-Token": CRON_TOKEN}
    response = client.post(
        "/oracle/admin/run-oracle-answer-feedback-pipeline",
        json={"dry_run": False, "clear_cache": False, "limit": 5000},
        headers=headers
    )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["ok"] is True
    assert res_json["dry_run"] is False
    assert res_json["report"]["summary_rows_written"] == 2
    
    # Assert token is not returned in the payload
    assert CRON_TOKEN not in str(res_json)
    
    called_mock = mock_run_backend if mock_run_backend.called else mock_run_scripts
    called_mock.assert_called_once()
    kwargs = called_mock.call_args[1]
    assert kwargs["dry_run"] is False
    assert kwargs["limit"] == 5000
    assert kwargs["clear_cache"] is False


def test_cron_limit_validation_capping():
    headers = {"X-Oracle-Answer-Pipeline-Cron-Token": CRON_TOKEN}
    # Send a limit above the 20000 cap (e.g. 50000)
    response = client.post(
        "/oracle/admin/run-oracle-answer-feedback-pipeline",
        json={"dry_run": True, "limit": 50000},
        headers=headers
    )
    
    # RunOracleAnswerPipelineRequest defines Field(..., le=20000), it should raise 422.
    assert response.status_code == 422
    err_type = response.json()["detail"][0]["type"]
    assert "validation_error" in err_type or "value_error" in err_type or "less_than_equal" in err_type
