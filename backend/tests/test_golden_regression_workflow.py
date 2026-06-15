from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "golden-oracle-regression.yml"

def read_workflow():
    return WORKFLOW.read_text(encoding="utf-8")

def test_bounded_autonomous_schedule_enabled():
    content = read_workflow()
    assert "schedule:" in content
    assert "workflow_dispatch:" in content
    assert "max two questions" in content.lower()

def test_max_questions_and_timeout_are_hard_capped():
    content = read_workflow()
    assert "-gt 2" in content
    assert "-gt 15" in content
    assert "timeout-minutes: 5" in content

def test_no_full_regression_or_promotion_or_db_write_steps():
    content = read_workflow()
    forbidden = [
        "run_golden_oracle_regression_cases.py",
        "build_golden_candidates_from_feedback.py",
        "promote_golden_candidates.py",
        "--source json",
        "--source db",
        "--write-db-run",
        "--write-report",
        "--rollback-mode verified-canary",
        "golden_oracle_regression_cases",
    ]
    for item in forbidden:
        assert item not in content

def test_single_attempt_no_retry_and_bounded_timeout():
    content = read_workflow()
    assert "--attempts 1" in content
    assert "infra-retries" not in content
    assert "retry" not in content.lower()
    assert "REQUEST_TIMEOUT_SECONDS" in content

def test_no_push_deploy_benchmark_or_wiki_writes():
    content = read_workflow().lower()
    assert "git push" not in content
    assert "deploy" not in content
    assert "benchmark" not in content
    assert "wiki_entries" not in content

def test_concurrency_cancellation_enabled():
    content = read_workflow()
    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content
