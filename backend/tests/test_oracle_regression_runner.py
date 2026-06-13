import sys
import os
import json
import pytest
import urllib.error
from unittest.mock import MagicMock, patch

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scripts.run_golden_oracle_regression_cases import run_regression

TEST_CASE = [{
    "id": "test_case",
    "source": "manual_regression",
    "question": "chiến dịch lệ giang diễn ra như thế nào?",
    "chapter_progress": 829,
    "intent": "event_plot",
    "must_not_contain": ["[DỮ LIỆU HỆ THỐNG]"],
    "must_contain_any": [],
    "semantic_forbidden_patterns": ["sông Lệ Giang"],
    "semantic_required_any_terms": ["chiến dịch"],
    "acceptable_abstain": True,
    "expected_abstain_text": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
    "status": "active"
}]


def run_runner_with_mock_responses_list(mock_responses_list, test_cases_list, extra_args=None):
    response_idx = 0

    def mock_urlopen(req, *args, **kwargs):
        nonlocal response_idx
        # Check URL
        url_str = req.full_url if hasattr(req, "full_url") else str(req)
        if "/api/health" in url_str:
            mock_health = MagicMock()
            mock_health.status = 200
            mock_health.read.return_value = json.dumps({"status": "ok", "git_commit": "mock_commit"}).encode("utf-8")
            mock_health.__enter__.return_value = mock_health
            return mock_health

        if response_idx >= len(mock_responses_list):
            res_item = mock_responses_list[-1]
        else:
            res_item = mock_responses_list[response_idx]
            response_idx += 1

        if isinstance(res_item, Exception):
            raise res_item

        status = 200
        body = {}
        if isinstance(res_item, tuple):
            status, body = res_item
        else:
            body = res_item

        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.read.return_value = json.dumps(body).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        return mock_resp

    original_open = open
    def mock_open(file, *args, **kwargs):
        if "golden_oracle_regression_cases.json" in str(file):
            m = MagicMock()
            m.__enter__.return_value.read.return_value = json.dumps(test_cases_list)
            return m
        return original_open(file, *args, **kwargs)

    argv = ["run_golden_oracle_regression_cases.py", "--base-url", "http://mock", "--write-report", "--infra-backoff-seconds", "0"]
    if extra_args:
        argv.extend(extra_args)

    with patch("urllib.request.urlopen", side_effect=mock_urlopen), \
         patch("builtins.open", new=mock_open), \
         patch("sys.argv", argv), \
         patch("backend.scripts.run_golden_oracle_regression_cases.json.dump") as mock_dump:

         report_data = None
         def save_report(data, f, *args, **kwargs):
             nonlocal report_data
             report_data = data
         mock_dump.side_effect = save_report

         exit_code = 0
         try:
             run_regression()
         except SystemExit as e:
             exit_code = e.code

         return exit_code, report_data


def test_golden_case_schema_valid():
    cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag", "golden_oracle_regression_cases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    assert len(cases) > 0
    for case in cases:
        assert "id" in case
        assert "source" in case
        assert "question" in case
        assert "chapter_progress" in case
        assert "intent" in case
        assert "must_not_contain" in case
        assert "must_contain_any" in case
        assert "semantic_forbidden_patterns" in case
        assert "semantic_required_any_terms" in case
        assert "acceptable_abstain" in case
        assert "expected_abstain_text" in case
        assert "status" in case


def test_runner_pass_with_abstain():
    mock_body = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body], TEST_CASE)
    assert exit_code == 0
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["results"][0]["passed"] is True
    assert report["summary"]["failure_class"] == "none"


def test_runner_fail_with_forbidden_pattern():
    mock_body = {
        "answer": "Trận chiến diễn ra ở sông Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body], TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["summary"]["semantic_failed"] == 1
    assert report["results"][0]["passed"] is False
    assert report["summary"]["failure_class"] == "semantic_failure"


def test_runner_fail_with_system_tag():
    mock_body = {
        "answer": "[DỮ LIỆU HỆ THỐNG]\nChưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body], TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
    assert report["summary"]["failure_class"] == "semantic_failure"


def test_runner_fail_without_required_terms():
    mock_body = {
        "answer": "Lệ Giang là khu vực rất đẹp.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body], TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
    assert report["summary"]["failure_class"] == "semantic_failure"


def test_runner_exits_3_when_no_cases():
    exit_code, report = run_runner_with_mock_responses_list([], [])
    assert exit_code == 3
    assert report["summary"]["failure_class"] == "configuration_failure"


def test_runner_exits_2_on_http_error():
    err = urllib.error.HTTPError("http://mock", 503, "Service Unavailable", {}, None)
    exit_code, report = run_runner_with_mock_responses_list([err, err, err, err], TEST_CASE)
    assert exit_code == 2
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["summary"]["infra_failed"] == 1
    assert report["results"][0]["passed"] is False
    assert "HTTP Error 503" in report["results"][0]["reason"]
    assert report["summary"]["failure_class"] == "infra_failure"


def test_runner_retry_success_on_timeout():
    # Attempt 1: Timeout, Attempt 2: Success
    timeout_err = TimeoutError("The read operation timed out")
    mock_body = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([timeout_err, mock_body], TEST_CASE)
    assert exit_code == 0
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["summary"]["retry_recovered"] == 1
    assert report["results"][0]["passed"] is True
    assert report["results"][0]["attempts"] == 2
    assert report["summary"]["failure_class"] == "none"


def test_runner_retry_success_on_503():
    # Attempt 1: 503, Attempt 2: Success
    err = urllib.error.HTTPError("http://mock", 503, "Service Unavailable", {}, None)
    mock_body = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([err, mock_body], TEST_CASE)
    assert exit_code == 0
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["summary"]["retry_recovered"] == 1
    assert report["results"][0]["passed"] is True
    assert report["results"][0]["attempts"] == 2


def test_runner_retry_success_on_429():
    # Attempt 1: 429, Attempt 2: Success
    err = urllib.error.HTTPError("http://mock", 429, "Too Many Requests", {}, None)
    mock_body = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([err, mock_body], TEST_CASE)
    assert exit_code == 0
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["summary"]["retry_recovered"] == 1
    assert report["results"][0]["passed"] is True
    assert report["results"][0]["attempts"] == 2


def test_runner_no_retry_on_semantic_failure():
    # If it is a semantic failure, we must NOT retry it even on attempt 1
    mock_body = {
        "answer": "Trận chiến diễn ra ở sông Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body, mock_body], TEST_CASE)
    assert exit_code == 1
    assert report["results"][0]["attempts"] == 1  # Should only run 1 attempt
    assert report["summary"]["failure_class"] == "semantic_failure"


def test_sql_migration_exists_and_contains_tables():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_path = os.path.join(repo_root, "sql", "create_oracle_golden_regression_registry.sql")
    assert os.path.exists(sql_path)
    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "oracle_golden_regression_cases" in content
    assert "oracle_golden_regression_runs" in content


def test_report_does_not_contain_secrets():
    mock_body = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_responses_list([mock_body], TEST_CASE)

    # Dump report to string and assert no standard secret keywords
    report_str = json.dumps(report)
    assert "Authorization" not in report_str
    assert "Bearer" not in report_str
    assert "token" not in report_str
    assert "secret" not in report_str
