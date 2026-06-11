import sys
import os
import json
import pytest
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

def run_runner_with_mock_response(mock_status, mock_body_dict, test_cases_list):
    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = mock_status
    mock_response.__enter__.return_value.read.return_value = json.dumps(mock_body_dict).encode("utf-8")
    
    original_open = open
    def mock_open(file, *args, **kwargs):
        if "golden_oracle_regression_cases.json" in str(file):
            m = MagicMock()
            m.__enter__.return_value.read.return_value = json.dumps(test_cases_list)
            return m
        return original_open(file, *args, **kwargs)
        
    with patch("urllib.request.urlopen", return_value=mock_response), \
         patch("builtins.open", new=mock_open), \
         patch("sys.argv", ["run_golden_oracle_regression_cases.py", "--base-url", "http://mock", "--write-report"]), \
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
    exit_code, report = run_runner_with_mock_response(200, mock_body, TEST_CASE)
    assert exit_code == 0
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 0
    assert report["results"][0]["passed"] is True
    assert "checks passed" in report["results"][0]["reason"]

def test_runner_fail_with_forbidden_pattern():
    mock_body = {
        "answer": "Trận chiến diễn ra ở sông Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_response(200, mock_body, TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
    assert "semantic forbidden pattern" in report["results"][0]["reason"]

def test_runner_fail_with_system_tag():
    mock_body = {
        "answer": "[DỮ LIỆU HỆ THỐNG]\nChưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_response(200, mock_body, TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
    assert "forbidden term" in report["results"][0]["reason"]

def test_runner_fail_without_required_terms():
    mock_body = {
        "answer": "Lệ Giang là khu vực rất đẹp.",
        "source": "local_wiki"
    }
    exit_code, report = run_runner_with_mock_response(200, mock_body, TEST_CASE)
    assert exit_code == 1
    assert report["summary"]["passed"] == 0
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
    assert "does not contain any semantic_required_any_terms" in report["results"][0]["reason"]

def test_runner_report_reasons():
    mock_body_pass = {
        "answer": "Chưa đủ dữ liệu trong truyện đã nạp để mô tả chắc chắn chiến dịch Lệ Giang.",
        "source": "local_wiki"
    }
    _, report_pass = run_runner_with_mock_response(200, mock_body_pass, TEST_CASE)
    assert report_pass["results"][0]["passed"] is True
    assert len(report_pass["results"][0]["reason"]) > 0
    
    mock_body_fail = {
        "answer": "Sông Lệ Giang",
        "source": "local_wiki"
    }
    _, report_fail = run_runner_with_mock_response(200, mock_body_fail, TEST_CASE)
    assert report_fail["results"][0]["passed"] is False
    assert len(report_fail["results"][0]["reason"]) > 0
