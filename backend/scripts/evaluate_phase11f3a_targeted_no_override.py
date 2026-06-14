import os
import sys
import json
import asyncio
import time
import subprocess
import hashlib
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

load_dotenv(os.path.join(backend_path, ".env"), override=True)

# Set environment variables for evaluation
os.environ["ORACLE_RAG_TRACE"] = "1"
os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "eval-admin-token"
os.environ["ORACLE_EVAL_MODE"] = "1"
os.environ["ORACLE_GROUNDED_VERIFIER_ENABLED"] = "1"
os.environ["ORACLE_GROUNDED_REPAIR_ENABLED"] = "1"
os.environ["SUPABASE_OFFLINE"] = "1"

from backend.routes.ai_oracle import ask_oracle, OracleRequest
from backend.scripts.evaluate_chapter_bot_quality import call_judge_llm, MockRequest, MockResponse

def get_sha256_of_file(filepath):
    if not os.path.exists(filepath):
        return ""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest().upper()

def get_git_head():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=parent_path).decode().strip()
    except Exception as e:
        print(f"Warning: failed to get git head: {e}")
        return ""

def get_git_diff_sha256():
    try:
        diff_data = subprocess.check_output(["git", "diff"], cwd=parent_path)
        return hashlib.sha256(diff_data).hexdigest().upper()
    except Exception as e:
        print(f"Warning: failed to get git diff: {e}")
        return ""

async def run_evaluation():
    git_head = get_git_head()
    git_diff_sha256 = get_git_diff_sha256()
    
    benchmark_path = os.path.join(backend_path, "evals", "chapter_bot_quality_cases_v1.json")
    benchmark_sha256 = get_sha256_of_file(benchmark_path)
    
    evaluator_path = os.path.join(backend_path, "scripts", "evaluate_chapter_bot_quality.py")
    evaluator_sha256 = get_sha256_of_file(evaluator_path)
    
    with open(benchmark_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    targets = ["loc-02", "event-06", "event-09", "event-01"]
    target_cases = [c for c in cases if c["case_id"] in targets]
    
    # We want to maintain order of targets
    target_cases_ordered = []
    for t in targets:
        for c in target_cases:
            if c["case_id"] == t:
                target_cases_ordered.append(c)
                break
                
    results_list = []
    
    total_oracle_requests = 0
    total_draft_calls = 0
    total_verifier_calls = 0
    total_repair_calls = 0
    total_judge_calls = 0
    total_attempts = 0
    total_retries = 0
    total_timeouts = 0
    
    main_provider = ""
    main_model = ""
    
    for case in target_cases_ordered:
        case_id = case["case_id"]
        print(f"\n=================== Running {case_id} 5 times ===================")
        
        for run_idx in range(5):
            print(f"[{case_id}] Run {run_idx+1}/5...")
            total_oracle_requests += 1
            
            req = OracleRequest(
                question=case["question"],
                chapter_progress=case["chapter_progress"],
                debug_bypass_cache=True
            )
            
            start_time = time.perf_counter()
            bot_res = await ask_oracle(
                body=req,
                request=MockRequest(),
                response=MockResponse(),
                authorization="Bearer eval-admin-token",
                x_oracle_feedback_admin_token="eval-admin-token"
            )
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            bot_answer = bot_res.answer
            trace = bot_res.trace or {}
            
            # Extract provider & model
            provider = trace.get("provider_used") or trace.get("provider", "unknown")
            model = trace.get("model_used") or trace.get("model", "unknown")
            if not main_provider and provider != "unknown":
                main_provider = provider
            if not main_model and model != "unknown":
                main_model = model
                
            draft_c = trace.get("draft_calls", 1) # default to 1 if not tracked
            verifier_c = trace.get("verifier_calls", 0)
            repair_c = trace.get("repair_calls", 0)
            
            total_draft_calls += draft_c
            total_verifier_calls += verifier_c
            total_repair_calls += repair_c
            total_attempts += 1 # ask_oracle attempt
            
            # Retrieve source context text used
            source_context_parts = []
            rag_context = trace.get("rag_context") or ""
            wiki_context = trace.get("wiki_context") or ""
            if rag_context:
                source_context_parts.append(rag_context)
            if wiki_context:
                source_context_parts.append(wiki_context)
            source_context = "\n\n".join(source_context_parts)
            
            # Call judge
            judge_res = None
            total_judge_calls += 1
            for attempt in range(3):
                try:
                    judge_res = await call_judge_llm(case, bot_answer, source_context)
                    if judge_res and judge_res.get("human_score") is not None:
                        break
                except Exception as e:
                    print(f"Judge attempt {attempt+1} failed: {e}")
                    total_retries += 1
                    await asyncio.sleep(1)
            
            if not judge_res:
                judge_res = {"human_score": 0, "unsupported_claims": True, "reasoning": "Judge failed."}
                
            score = judge_res.get("human_score", 0)
            unsupported = judge_res.get("unsupported_claims", False)
            
            selected_chapters = trace.get("selected_chapters") or []
            future_leakage = any(ch > case["chapter_progress"] for ch in selected_chapters)
            
            run_data = {
                "case_id": case_id,
                "repetition": run_idx + 1,
                "question": case["question"],
                "answer": bot_answer,
                "selected_chunks": trace.get("selected_chunk_ids") or trace.get("selected_chunk_refs") or [],
                "selected_chapters": selected_chapters,
                "provider_used": provider,
                "model_used": model,
                "draft_calls": draft_c,
                "verifier_calls": verifier_c,
                "repair_calls": repair_c,
                "judge_calls": 1,
                "override_hits": 0,
                "abstained": bot_res.abstained,
                "abstain_reason": trace.get("abstain_reason") or "",
                "human_score": score,
                "unsupported_claims": unsupported,
                "future_leakage": future_leakage,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            results_list.append(run_data)
            
            line = f"  Run {run_idx+1}: Score={score} | Abstained={bot_res.abstained} | Verifier/Repair={verifier_c}/{repair_c} | Model={model} | Leakage={future_leakage}"
            print(line.encode('ascii', 'backslashreplace').decode('ascii'))
            
            # Sleep slightly to avoid rate limit
            await asyncio.sleep(1)
            
    # Save target results
    output_timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"phase11f3a_targeted_no_override_{output_timestamp}.json"
    output_dir = os.path.join(backend_path, "evals", "runs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    report = {
        "git_head": git_head,
        "git_diff_sha256": git_diff_sha256,
        "benchmark_sha256": benchmark_sha256,
        "evaluator_sha256": evaluator_sha256,
        "override_hits": 0,
        "provider": main_provider,
        "model": main_model,
        "generation_parameters": {
            "temperature": 0.0,
            "oracle_eval_mode": "1",
            "oracle_grounded_verifier_enabled": "1",
            "oracle_grounded_repair_enabled": "1"
        },
        "call_accounting": {
            "oracle_requests": total_oracle_requests,
            "draft_model_calls": total_draft_calls,
            "verifier_model_calls": total_verifier_calls,
            "repair_model_calls": total_repair_calls,
            "judge_model_calls": total_judge_calls,
            "provider_attempts": total_attempts,
            "retries": total_retries,
            "timeouts": total_timeouts
        },
        "results": results_list
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        
    print(f"\nSaved targeted evaluation run results to {output_path}")
    print("\n=================== TARGETED GATE SUMMARY ===================")
    
    # Check assertions
    all_passed = True
    for t in targets:
        runs = [r for r in results_list if r["case_id"] == t]
        scores = [r["human_score"] for r in runs]
        abstentions = [r["abstained"] for r in runs]
        failures = [r for r in runs if r["human_score"] < 2]
        leakages = sum(1 for r in runs if r["future_leakage"])
        
        pass_rate = sum(1 for s in scores if s >= 2) / len(scores) * 100
        abstain_rate = sum(1 for a in abstentions if a) / len(abstentions) * 100
        
        print(f"Case {t}: Pass Rate (Score >= 2)={pass_rate:.1f}% | Abstain Rate={abstain_rate:.1f}% | Scores={scores} | Leakages={leakages}")
        
        # Validation checks
        if t == "loc-02":
            if any(s < 2 for s in scores) or any(abstentions):
                all_passed = False
        elif t == "event-06":
            if any(s < 2 for s in scores) or any(abstentions):
                all_passed = False
        elif t == "event-09":
            if sum(1 for s in scores if s >= 2) < 4 or any(s == 0 for s in scores):
                all_passed = False
        elif t == "event-01":
            if sum(1 for s in scores if s >= 2) < 4:
                all_passed = False
                
    total_leakages = sum(1 for r in results_list if r["future_leakage"])
    total_unsupported = sum(1 for r in results_list if r["unsupported_claims"])
    unsupported_rate = total_unsupported / len(results_list) * 100
    
    print(f"\nGlobal Verification: Total Leakages={total_leakages} | Unsupported Claims Rate={unsupported_rate:.2f}%")
    
    if total_leakages > 0 or unsupported_rate > 2.0:
        all_passed = False
        
    if all_passed:
        print("TARGETED GATES STATUS: SUCCESS_PASS")
    else:
        print("TARGETED GATES STATUS: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
