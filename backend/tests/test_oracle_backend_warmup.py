import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch

# Ensure repo root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scripts.warm_up_oracle_backend import main as warmup_main


def run_warmup_with_mock_responses(mock_responses_list, extra_args=None):
    response_idx = 0
    
    def mock_urlopen(req, *args, **kwargs):
        nonlocal response_idx
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

    argv = ["warm_up_oracle_backend.py", "--base-url", "http://mock", "--backoff-seconds", "0"]
    if extra_args:
        argv.extend(extra_args)

    with patch("urllib.request.urlopen", side_effect=mock_urlopen), \
         patch("sys.argv", argv):
         
         exit_code = 0
         try:
             warmup_main()
         except SystemExit as e:
             exit_code = e.code
         return exit_code


def test_warmup_success_first_attempt():
    mock_body = {
        "status": "ok",
        "git_commit": "8471f7e"
    }
    exit_code = run_warmup_with_mock_responses([mock_body])
    assert exit_code == 0


def test_warmup_success_with_delay():
    # First attempt: Timeout exception, Second attempt: Success
    timeout_err = TimeoutError("The read operation timed out")
    mock_body = {
        "status": "ok",
        "git_commit": "8471f7e"
    }
    exit_code = run_warmup_with_mock_responses([timeout_err, mock_body], ["--attempts", "3"])
    assert exit_code == 0


def test_warmup_failure_exhausted_attempts():
    timeout_err = TimeoutError("The read operation timed out")
    exit_code = run_warmup_with_mock_responses([timeout_err, timeout_err, timeout_err], ["--attempts", "3"])
    assert exit_code == 2  # Exit code 2 for infra failure


def test_warmup_failure_json_not_ok():
    # Returns 200 but status is not "ok"
    mock_body = {
        "status": "maintenance"
    }
    exit_code = run_warmup_with_mock_responses([mock_body], ["--attempts", "2"])
    assert exit_code == 2
