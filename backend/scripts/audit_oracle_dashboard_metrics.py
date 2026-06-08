import os
import sys
import json
from pathlib import Path

# Force UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "backend"))

from backend.database import supabase

def run_audit():
    print("Starting Oracle Dashboard Metrics Consistency Audit...")
    
    audit_results = {}
    
    # 1. Query: rag_feedback count by status
    print("Querying rag_feedback count by status...")
    status_counts = {}
    statuses = ['pending', 'reviewed', 'accepted', 'rejected', 'resolved']
    for status in statuses:
        try:
            res = supabase.table("rag_feedback").select("id", count="exact").eq("status", status).limit(1).execute()
            status_counts[status] = res.count or 0
        except Exception as e:
            print(f"Error querying status {status}: {e}")
            status_counts[status] = 0
    audit_results["rag_feedback_count_by_status"] = status_counts
    
    # 2. Query: rag_feedback count by feedback_type
    print("Querying rag_feedback count by feedback_type...")
    type_counts = {}
    feedback_types = ['wrong', 'missing', 'spoiler', 'hallucination', 'other']
    for ftype in feedback_types:
        try:
            res = supabase.table("rag_feedback").select("id", count="exact").eq("feedback_type", ftype).limit(1).execute()
            type_counts[ftype] = res.count or 0
        except Exception as e:
            print(f"Error querying feedback_type {ftype}: {e}")
            type_counts[ftype] = 0
    audit_results["rag_feedback_count_by_feedback_type"] = type_counts
    
    # 3. Query: rag_feedback count by status + feedback_type
    print("Querying rag_feedback count by status + feedback_type...")
    status_type_counts = {}
    for status in statuses:
        status_type_counts[status] = {}
        for ftype in feedback_types:
            try:
                res = supabase.table("rag_feedback").select("id", count="exact").eq("status", status).eq("feedback_type", ftype).limit(1).execute()
                status_type_counts[status][ftype] = res.count or 0
            except Exception as e:
                print(f"Error querying status+type {status}+{ftype}: {e}")
                status_type_counts[status][ftype] = 0
    audit_results["rag_feedback_count_by_status_and_type"] = status_type_counts
    
    # 4. Query: oracle_answer_feedback_summary count
    print("Querying oracle_answer_feedback_summary count...")
    summary_count = 0
    try:
        # Check if table exists by querying it
        res = supabase.table("oracle_answer_feedback_summary").select("query_pattern", count="exact").limit(1).execute()
        summary_count = res.count or 0
    except Exception as e:
        print(f"Error or table does not exist oracle_answer_feedback_summary: {e}")
    audit_results["oracle_answer_feedback_summary_count"] = summary_count
    
    # 5. Query: oracle_answer_effective_patches count by effective_status
    print("Querying oracle_answer_effective_patches count by effective_status...")
    patch_counts = {}
    patch_statuses = ['active', 'disabled']
    for pstatus in patch_statuses:
        try:
            res = supabase.table("oracle_answer_effective_patches").select("id", count="exact").eq("effective_status", pstatus).limit(1).execute()
            patch_counts[pstatus] = res.count or 0
        except Exception as e:
            print(f"Error or table does not exist oracle_answer_effective_patches: {e}")
            patch_counts[pstatus] = 0
    audit_results["oracle_answer_effective_patches_count_by_status"] = patch_counts
    
    # 6. Save results to backend/rag/generated_oracle_dashboard_metrics_audit.json
    output_path = REPO_ROOT / "backend" / "rag" / "generated_oracle_dashboard_metrics_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
        
    print(f"Audit completed. Results saved to {output_path}")

if __name__ == "__main__":
    run_audit()
