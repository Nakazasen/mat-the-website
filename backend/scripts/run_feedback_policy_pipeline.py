import os
import sys
import json
import argparse
from typing import Dict, List, Any

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

try:
    from main import supabase
except ImportError:
    from backend.main import supabase

from backend.rag.provisional_feedback_aggregator import summarize_feedback
from backend.rag.effective_patch_engine import build_patch_payloads, patch_dedupe_key

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def fetch_feedback_records(limit: int, since_hours: int = None, supabase_client=None) -> List[Dict[str, Any]]:
    client = supabase_client if supabase_client is not None else supabase
    try:
        query = client.table("provisional_library_feedback").select("*")
        if since_hours:
            import datetime
            cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=since_hours)
            query = query.gte("created_at", cutoff.isoformat())
        res = query.limit(limit).execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching feedback from Supabase: {e}")
        return []

def fetch_provisional_records(pids: List[str], supabase_client=None) -> Dict[str, Dict[str, Any]]:
    if not pids:
        return {}
    client = supabase_client if supabase_client is not None else supabase
    try:
        records = {}
        batch_size = 100
        for i in range(0, len(pids), batch_size):
            batch = pids[i:i+batch_size]
            res = client.table("provisional_library").select("*").in_("id", batch).execute()
            for r in (res.data or []):
                if r.get("id"):
                    records[r["id"]] = r
        return records
    except Exception as e:
        print_safe(f"Error fetching provisional records: {e}")
        return {}

def fetch_existing_active_patches(supabase_client=None) -> List[Dict[str, Any]]:
    client = supabase_client if supabase_client is not None else supabase
    try:
        res = client.table("provisional_library_effective_patches").select("*").eq("effective_status", "active").execute()
        return res.data or []
    except Exception as e:
        print_safe(f"Error fetching existing active patches: {e}")
        return []

def write_summaries(summaries: List[Dict[str, Any]], dry_run: bool, supabase_client=None) -> Dict[str, Any]:
    stats = {"upserted": 0, "failed": 0, "errors": []}
    if not summaries:
        return stats

    if dry_run:
        stats["upserted"] = len(summaries)
        return stats

    client = supabase_client if supabase_client is not None else supabase
    batch_size = 100
    for i in range(0, len(summaries), batch_size):
        batch = summaries[i:i+batch_size]
        try:
            res = client.table("provisional_library_feedback_summary").upsert(batch).execute()
            stats["upserted"] += len(res.data or [])
        except Exception as e:
            stats["failed"] += len(batch)
            stats["errors"].append(str(e))
            
    return stats

def write_patches(patches: List[Dict[str, Any]], dry_run: bool, supabase_client=None) -> Dict[str, Any]:
    stats = {"upserted": 0, "failed": 0, "errors": []}
    if not patches:
        return stats

    if dry_run:
        stats["upserted"] = len(patches)
        return stats

    client = supabase_client if supabase_client is not None else supabase
    cleaned_patches = []
    for p in patches:
        clean = dict(p)
        for k, v in clean.items():
            if isinstance(v, set):
                clean[k] = list(v)
        cleaned_patches.append(clean)

    batch_size = 100
    for i in range(0, len(cleaned_patches), batch_size):
        batch = cleaned_patches[i:i+batch_size]
        try:
            res = client.table("provisional_library_effective_patches").insert(batch).execute()
            stats["upserted"] += len(res.data or [])
        except Exception as e:
            stats["failed"] += len(batch)
            stats["errors"].append(str(e))
            
    return stats

def clear_selective_oracle_cache(target_names: List[str], dry_run: bool, supabase_client=None) -> int:
    if not target_names:
        return 0
    client = supabase_client if supabase_client is not None else supabase
    try:
        # Fetch all cache entries
        res = client.table("oracle_cache").select("id, response").execute()
        cache_entries = res.data or []
        
        ids_to_delete = []
        for entry in cache_entries:
            resp = (entry.get("response") or "").lower()
            for name in target_names:
                if name.lower() in resp:
                    ids_to_delete.append(entry["id"])
                    break
        
        if ids_to_delete and not dry_run:
            batch_size = 100
            for i in range(0, len(ids_to_delete), batch_size):
                batch = ids_to_delete[i:i+batch_size]
                client.table("oracle_cache").delete().in_("id", batch).execute()
                
        return len(ids_to_delete)
    except Exception as e:
        print_safe(f"Error clearing cache selectively: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Run feedback summary, patch building, and cache invalidation pipeline.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run (no DB write).")
    parser.add_argument("--write", action="store_true", help="Commit summaries and patches to the database.")
    parser.add_argument("--limit", type=int, default=5000, help="Limit maximum feedback rows to fetch.")
    parser.add_argument("--json", action="store_true", help="Format console summary output as JSON.")
    parser.add_argument("--clear-cache", action="store_true", help="Selectively clear oracle cache for patched entities.")
    parser.add_argument("--since-hours", type=int, help="Limit feedback records to those created within since-hours.")
    parser.add_argument("--log-run", action="store_true", help="Log pipeline run status in database.")
    parser.add_argument("--trigger-source", choices=["github_actions", "manual", "cron_endpoint", "local"], default="local", help="Pipeline execution trigger source.")
    
    args = parser.parse_args()
    
    dry_run = True
    if args.write and not args.dry_run:
        dry_run = False

    report = run_feedback_policy_pipeline(
        supabase,
        dry_run=dry_run,
        limit=args.limit,
        clear_cache=args.clear_cache,
        since_hours=args.since_hours,
        log_run=args.log_run,
        trigger_source=args.trigger_source
    )

    if args.json:
        print_safe(json.dumps(report, indent=2))
    else:
        status_label = "WOULD WRITE" if dry_run else "WRITTEN"
        cache_label = "WOULD DELETE" if dry_run else "DELETED"
        print_safe("-" * 60)
        print_safe("FEEDBACK POLICY PIPELINE REPORT:")
        print_safe(f"Mode: {'DRY-RUN (Simulated)' if dry_run else 'WRITE (Supabase Commit)'}")
        print_safe(f"Feedback rows read: {report['feedback_rows_read']}")
        print_safe(f"Summaries built: {report['summary_rows_built']} ({status_label}: {report['summary_rows_written']})")
        print_safe(f"Patches generated: {report['patches_built']} ({status_label}: {report['patches_written']})")
        print_safe(f"Cache rows deleted: {report['cache_rows_deleted']} ({cache_label})")
        print_safe("-" * 60)

def run_feedback_policy_pipeline(
    supabase_client,
    dry_run: bool,
    limit: int = 5000,
    clear_cache: bool = True,
    since_hours: int = None,
    log_run: bool = False,
    trigger_source: str = "unknown"
) -> dict:
    import datetime
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    errors = []
    feedback_rows_read = 0
    summary_rows_written = 0
    patches_written = 0
    cache_rows_deleted = 0
    summaries_built = 0
    patches_built = 0
    ok = False
    report = {}

    try:
        # 1. Fetch Feedback
        feedback_rows = fetch_feedback_records(limit, since_hours, supabase_client=supabase_client)
        feedback_rows_read = len(feedback_rows)

        # 2. Build Feedback Summaries
        summaries = summarize_feedback(feedback_rows)
        summaries_built = len(summaries)

        # 3. Fetch target provisional records
        pids = list(set(str(row["provisional_id"]) for row in feedback_rows if row.get("provisional_id")))
        provisional_records = fetch_provisional_records(pids, supabase_client=supabase_client)

        # 4. Build Knowledge Patches
        generated_patches = build_patch_payloads(feedback_rows, provisional_records)
        patches_built = len(generated_patches)

        # 5. Idempotency Check
        existing_patches = fetch_existing_active_patches(supabase_client=supabase_client)
        existing_keys = {patch_dedupe_key(p) for p in existing_patches}

        new_patches = []
        for p in generated_patches:
            key = patch_dedupe_key(p)
            if key not in existing_keys:
                new_patches.append(p)
                existing_keys.add(key)  # Avoid adding duplicates within the same run

        # 6. Database Writes
        summary_stats = write_summaries(summaries, dry_run=dry_run, supabase_client=supabase_client)
        summary_rows_written = summary_stats["upserted"]
        if summary_stats.get("errors"):
            errors.extend(summary_stats["errors"])

        patch_stats = write_patches(new_patches, dry_run=dry_run, supabase_client=supabase_client)
        patches_written = patch_stats["upserted"]
        if patch_stats.get("errors"):
            errors.extend(patch_stats["errors"])

        # Update feedback status to 'resolved'
        feedback_ids = [fb.get("id") for fb in feedback_rows if fb.get("id")]
        if feedback_ids and not dry_run:
            try:
                supabase_client.table("provisional_library_feedback").update({"status": "resolved"}).in_("id", feedback_ids).execute()
            except Exception as e:
                errors.append(f"Failed to resolve library feedbacks: {e}")

        # 7. Collect names for cache clearing
        target_names_to_clear = set()
        for p in generated_patches:
            tn = p.get("target_name")
            if tn and len(tn) >= 2:
                target_names_to_clear.add(tn)

            qp = p.get("query_pattern")
            if qp:
                # Extract basic entity name from patterns like "Hàn Phong là ai?"
                clean_qp = qp.replace(" là ai?", "").replace(" là gì?", "").strip()
                if len(clean_qp) >= 2:
                    target_names_to_clear.add(clean_qp)

        # 8. Cache Invalidation
        if clear_cache and target_names_to_clear:
            cache_rows_deleted = clear_selective_oracle_cache(list(target_names_to_clear), dry_run=dry_run, supabase_client=supabase_client)

        ok = len(errors) == 0
        report = {
            "feedback_rows_read": feedback_rows_read,
            "summary_rows_built": summaries_built,
            "summary_rows_written": summary_rows_written,
            "patches_built": patches_built,
            "patches_written": patches_written,
            "cache_rows_deleted": cache_rows_deleted,
            "dry_run": dry_run
        }
    except Exception as e:
        errors.append(str(e))
        ok = False
        report = {
            "feedback_rows_read": feedback_rows_read,
            "summary_rows_built": 0,
            "summary_rows_written": 0,
            "patches_built": 0,
            "patches_written": 0,
            "cache_rows_deleted": 0,
            "dry_run": dry_run
        }
    finally:
        finished_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if log_run:
            try:
                run_payload = {
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "trigger_source": trigger_source,
                    "dry_run": dry_run,
                    "clear_cache": clear_cache,
                    "feedback_rows_read": feedback_rows_read,
                    "summary_rows_written": summary_rows_written,
                    "patches_written": patches_written,
                    "cache_rows_deleted": cache_rows_deleted,
                    "ok": ok,
                    "errors": errors,
                    "report": report
                }
                supabase_client.table("feedback_policy_pipeline_runs").insert(run_payload).execute()
            except Exception as log_err:
                print_safe(f"Failed to log pipeline run: {log_err}")

    if not ok and errors:
        raise RuntimeError(f"Pipeline finished with errors: {', '.join(errors)}")

    return report

if __name__ == "__main__":
    main()
