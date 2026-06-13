import os
import re

def test_golden_regression_workflow_rules():
    workflow_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        ".github", "workflows", "golden-oracle-regression.yml"
    )
    assert os.path.exists(workflow_path), f"Workflow file not found at {workflow_path}"
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 13. workflow không trigger pull_request
    assert "pull_request" not in content
    assert "schedule:" in content
    assert "cron:" in content
    assert "workflow_dispatch:" in content

    # 14. workflow permissions contents read
    assert re.search(r"permissions:\s*\n\s*contents:\s*read", content, re.IGNORECASE) or \
           re.search(r"contents:\s*read", content, re.IGNORECASE)

    # 15. workflow có concurrency
    assert "concurrency:" in content
    assert "group: golden-oracle-regression-production" in content
    assert "cancel-in-progress: false" in content

    # Check timeout-minutes
    assert "timeout-minutes: 15" in content

    # 16. artifacts upload if always
    upload_occurrences = content.count("actions/upload-artifact@v4")
    always_occurrences = content.count("if: always()")
    assert upload_occurrences >= 3
    assert always_occurrences >= 3

    # 17. secret không nằm literal trong YAML
    forbidden_keywords = ["SUPABASE_KEY=eyJ", "SUPABASE_URL=https://"]
    for kw in forbidden_keywords:
        assert kw not in content

    # 10. workflow có JSON source
    assert "--source json" in content
    # 11. workflow có DB source
    assert "--source db" in content
    # 12. workflow DB rollout dùng rollback-mode off cho cả hai
    assert "--rollback-mode off" in content
    assert "--rollback-mode verified-canary" not in content

    # 13. Candidate Intake steps (dry-run, no --write)
    assert "build_golden_candidates_from_feedback.py" in content
    assert "promote_golden_candidates.py" in content
    
    # Check that --write is not passed to builder/promoter steps
    # We locate build_golden_candidates_from_feedback.py and check that the line/command doesn't contain --write
    # We do the same for promote_golden_candidates.py
    builder_match = re.search(r"build_golden_candidates_from_feedback\.py.*", content)
    assert builder_match is not None
    assert "--write" not in builder_match.group(0)
    
    promoter_match = re.search(r"promote_golden_candidates\.py(\s|\\|\w|-|\.|\/|:)*", content)
    assert promoter_match is not None
    assert "--write" not in promoter_match.group(0)
    
    assert "feedback-to-golden-promotion-report" in content

    # 14. Containment attributes in combined summary inline python script
    assert "autonomous_write_enabled" in content
    assert "candidate_intake_mode" in content
    assert "promotion_mode" in content
