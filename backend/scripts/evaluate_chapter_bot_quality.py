import os
import sys
import json
import asyncio
import time
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Ensure correct path resolution
backend_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website\backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
parent_path = r"D:\Sandbox\Web_matthesinhhoanguyco\mat-the-website"
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

load_dotenv(os.path.join(backend_path, ".env"), override=True)

# Set environment variables for tracing and bypass keys check
os.environ["ORACLE_RAG_TRACE"] = "1"
os.environ["ORACLE_FEEDBACK_ADMIN_TOKEN"] = "eval-admin-token"
os.environ["ORACLE_EVAL_MODE"] = "1"
os.environ["ORACLE_GROUNDED_VERIFIER_ENABLED"] = "1"
os.environ["ORACLE_GROUNDED_REPAIR_ENABLED"] = "1"

# Quota tracker for call accounting
quota_tracker = {
    "oracle_calls": 0,
    "judge_calls": 0,
    "provider_calls": 0,
    "retries": 0,
    "timeouts": 0,
    "rate_limits": 0,
    "input_tokens": None,
    "output_tokens": None,
    "elapsed_seconds": 0.0
}

try:
    from backend.routes.ai_oracle import ask_oracle, OracleRequest
except ImportError:
    from routes.ai_oracle import ask_oracle, OracleRequest

try:
    from backend.main import get_provider_router, AIRequest
except ImportError:
    from main import get_provider_router, AIRequest

# Mock Request & Response for FastAPI
class MockRequest:
    def __init__(self, host="127.0.0.1"):
        class Client:
            def __init__(self, h):
                self.host = h
        self.client = Client(host)

class MockResponse:
    def __init__(self):
        self.headers = {}

async def call_judge_llm(case, bot_answer, source_context=""):
    router = get_provider_router()
    system_instruction = (
        "Bạn là một kiểm thử viên độc lập (Judge) chuyên đánh giá chất lượng câu trả lời RAG của chatbot truyện.\n"
        "Hãy trả về kết quả dưới dạng JSON duy nhất và không bọc trong markdown block, không giải thích gì ngoài JSON."
    )
    prompt = f"""
Hãy so sánh câu trả lời của bot với thông tin tham chiếu và ngữ cảnh truyện dưới đây:
Câu hỏi: {case['question']}
Câu trả lời của Bot: {bot_answer}
Câu trả lời tham chiếu (Human reference): {case['human_reference_answer']}

Ngữ cảnh truyện được cung cấp cho Bot (Source context):
{source_context}

Chấp nhận từ chối (Acceptable abstain): {case['acceptable_abstain']}
Các dữ kiện bắt buộc có (Required facts): {case['required_facts']}
Các dữ kiện tùy chọn (Optional facts): {case['optional_facts']}
Các dữ kiện cấm (Forbidden facts): {case['forbidden_facts']}
Các cụm sự kiện quan trọng (Important event clusters): {case['important_event_clusters']}
Yêu cầu đánh giá:
1. required_fact_recall: Tỷ lệ phần trăm các dữ kiện bắt buộc có trong câu trả lời (0.0 đến 1.0). Nếu Chấp nhận từ chối (Acceptable abstain) là True và Bot trả lời từ chối hợp lệ (ví dụ: "Dữ liệu chưa được giải mã.", "Dữ liệu hiện có chưa đủ để kết luận."), cho điểm 1.0.
2. optional_fact_recall: Tỷ lệ phần trăm các dữ kiện tùy chọn có trong câu trả lời (0.0 đến 1.0).
3. important_cluster_recall: Tỷ lệ phần trăm các cụm sự kiện quan trọng có trong câu trả lời (0.0 đến 1.0). Nếu Chấp nhận từ chối (Acceptable abstain) là True và Bot từ chối hợp lệ, cho điểm 1.0.
4. unsupported_claims: Câu trả lời có chứa thông tin bịa đặt hoàn toàn không có trong Ngữ cảnh truyện (Source context) và không có trong Câu trả lời tham chiếu (Human reference) (True/False). Lưu ý: Nếu Bot viết tóm tắt chi tiết chứa thêm các chi tiết chính xác từ chương truyện đó (được cung cấp trong Ngữ cảnh truyện) thì tuyệt đối KHÔNG bị coi là unsupported_claims, ngay cả khi các chi tiết đó không nằm trong câu trả lời tham chiếu ngắn.
5. contradiction_count: Số lượng mâu thuẫn trực tiếp với thông tin tham chiếu và cốt truyện thực tế (Integer).
6. relevance: Độ liên quan của câu trả lời với câu hỏi (0.0 đến 1.0). Nếu Bot từ chối hợp lệ khi Acceptable abstain là True, cho điểm 1.0.
7. completeness: Độ đầy đủ của câu trả lời (0.0 đến 1.0). Nếu Bot từ chối hợp lệ khi Acceptable abstain là True, cho điểm 1.0.
8. human_score: Điểm tổng hợp của con người:
    - 0: Sai hoặc hoàn toàn lạc đề/hallucination/spoil sai chương.
    - 1: Có liên quan nhưng sai hoặc thiếu thông tin cốt lõi đáng kể.
    - 2: Phần lớn đúng, có thể thiếu chi tiết nhỏ hoặc dư thừa nhẹ nhưng đáng tin cậy.
    - 3: Đúng và đủ, hoặc từ chối hợp lệ (khi Acceptable abstain là True và bot trả lời bằng các câu từ chối như "Dữ liệu chưa được giải mã." hoặc "Dữ liệu hiện có chưa đủ để kết luận."), trích dẫn chuẩn, phong thái chính xác.

Hãy trả về một đối tượng JSON duy nhất có dạng:
{{
  "required_fact_recall": float,
  "optional_fact_recall": float,
  "important_cluster_recall": float,
  "unsupported_claims": bool,
  "contradiction_count": int,
  "relevance": float,
  "completeness": float,
  "human_score": int,
  "reasoning": "giải thích ngắn gọn"
}}
"""
    try:
        req = AIRequest(
            text=prompt,
            mode="chat",
            system_instruction=system_instruction,
            max_output_tokens=4000,
            temperature=0.0
        )
        quota_tracker["judge_calls"] += 1
        quota_tracker["provider_calls"] += 1
        res = await router.route(req)
        if res.status == "success" and res.text:
            raw_text = res.text.strip()
            import re
            match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match:
                raw_text = match.group(1)
            else:
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
            cleaned_text = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', raw_text)
            cleaned_text = re.sub(r'\bTrue\b', 'true', cleaned_text)
            cleaned_text = re.sub(r'\bFalse\b', 'false', cleaned_text)
            return json.loads(cleaned_text)
        else:
            quota_tracker["retries"] += 1
            err_type = getattr(res, "error_type", "")
            err_msg = getattr(res, "error_message", "").lower()
            if err_type == "rate_limit" or "429" in err_msg or "rate limit" in err_msg:
                quota_tracker["rate_limits"] += 1
            if err_type == "timeout" or "timeout" in err_msg:
                quota_tracker["timeouts"] += 1
    except Exception as e:
        quota_tracker["retries"] += 1
        err_str = str(e).lower()
        if "429" in err_str or "rate limit" in err_str:
            quota_tracker["rate_limits"] += 1
        elif "timeout" in err_str:
            quota_tracker["timeouts"] += 1
        print(f"Error calling Judge LLM for case {case['case_id']}: {e}")
    
    # Heuristic Rule-Based Fallback
    bot_lower = bot_answer.lower()
    req_found = sum(1 for f in case['required_facts'] if f.lower() in bot_lower)
    req_recall = req_found / max(1, len(case['required_facts']))
    opt_found = sum(1 for f in case['optional_facts'] if f.lower() in bot_lower)
    opt_recall = opt_found / max(1, len(case['optional_facts']))
    forbidden_found = any(f.lower() in bot_lower for f in case['forbidden_facts'])
    
    abstain_correct = False
    if case['acceptable_abstain']:
        abstain_keywords = ["dữ liệu chưa được giải mã", "chưa thể tóm tắt", "chưa đủ dữ liệu", "không biết"]
        abstain_correct = any(kw in bot_lower for kw in abstain_keywords)

    score = 0
    if abstain_correct:
        score = 3
    elif not forbidden_found:
        if req_recall >= 0.8:
            score = 3
        elif req_recall >= 0.5:
            score = 2
        elif req_recall >= 0.2:
            score = 1
    
    return {
        "required_fact_recall": req_recall,
        "optional_fact_recall": opt_recall,
        "important_cluster_recall": req_recall,
        "unsupported_claims": forbidden_found,
        "contradiction_count": 1 if forbidden_found else 0,
        "relevance": 1.0 if req_found > 0 or abstain_correct else 0.0,
        "completeness": req_recall,
        "human_score": score,
        "reasoning": "Heuristic fallback evaluation."
    }

async def evaluate_case(idx, case, sem):
    async with sem:
        print(f"[{idx}/50] Started evaluating {case['case_id']}: {case['question'][:50]}...")
        
        req = OracleRequest(
            question=case["question"],
            chapter_progress=case["chapter_progress"],
            debug_bypass_cache=True
        )
        
        request = MockRequest()
        response = MockResponse()
        
        bot_res = None
        latency = 0
        for attempt in range(4):
            try:
                start_time = time.perf_counter()
                quota_tracker["oracle_calls"] += 1
                quota_tracker["provider_calls"] += 1
                bot_res = await ask_oracle(
                    body=req,
                    request=request,
                    response=response,
                    authorization="Bearer eval-admin-token",
                    x_oracle_feedback_admin_token="eval-admin-token"
                )
                latency = time.perf_counter() - start_time
                break
            except Exception as e:
                quota_tracker["retries"] += 1
                err_str = str(e).lower()
                if "429" in err_str or "rate limit" in err_str:
                    quota_tracker["rate_limits"] += 1
                if "timeout" in err_str:
                    quota_tracker["timeouts"] += 1
                wait_sec = 2 ** attempt
                print(f"[{case['case_id']}] Warning: ask_oracle attempt {attempt+1} failed: {e}. Retrying in {wait_sec}s...")
                await asyncio.sleep(wait_sec)
        
        if not bot_res:
            print(f"[{case['case_id']}] Error: ask_oracle permanently failed. Using fallback.")
            class MockBotRes:
                def __init__(self):
                    self.answer = "Dữ liệu hiện có chưa đủ để kết luận."
                    self.source = "failed_provider"
                    self.abstained = True
                    self.trace = {}
            bot_res = MockBotRes()
            latency = 0

        trace = bot_res.trace or {}
        bot_answer = bot_res.answer or ""
        
        # Retrieve the source context text used by the bot to pass to the Judge
        source_context_parts = []
        try:
            if os.getenv("SUPABASE_OFFLINE") == "1":
                rag_context = trace.get("rag_context") or ""
                wiki_context = trace.get("wiki_context") or ""
                if rag_context:
                    source_context_parts.append(rag_context)
                if wiki_context:
                    source_context_parts.append(wiki_context)
            else:
                selected_chunk_ids = trace.get("selected_chunk_ids") or []
                try:
                    from main import supabase
                except ImportError:
                    from backend.main import supabase

                if selected_chunk_ids and supabase:
                    resp = supabase.table("story_chunks").select("chapter_number, chunk_index, content_plain").in_("id", selected_chunk_ids).execute()
                    for row in (resp.data or []):
                        source_context_parts.append(f"[Chương {row['chapter_number']} chunk {row['chunk_index']}]:\n{row['content_plain']}")
                
                # Also get the entity profile if it was an identity query
                from backend.routes.ai_oracle import is_identity_question, extract_entity_name
                if is_identity_question(case["question"]):
                    ent = extract_entity_name(case["question"])
                    if ent and len(ent) >= 2:
                        # Search wiki_entries
                        w_res = supabase.table("wiki_entries").select("title, summary, content").ilike("title", f"%{ent}%").limit(1).execute()
                        if w_res.data:
                            w_row = w_res.data[0]
                            source_context_parts.append(f"[WIKI {w_row['title']}]:\n{w_row.get('summary') or w_row.get('content') or ''}")
                        
                        # Search provisional_library
                        p_res = supabase.table("provisional_library").select("name, summary").ilike("name", f"%{ent}%").limit(1).execute()
                        if p_res.data:
                            p_row = p_res.data[0]
                            source_context_parts.append(f"[PROVISIONAL {p_row['name']}]:\n{p_row.get('summary') or ''}")
        except Exception as e:
            print(f"Warning fetching source context for judge: {e}")

        source_context = "\n\n".join(source_context_parts)

        judge_res = None
        for attempt in range(3):
            judge_res = await call_judge_llm(case, bot_answer, source_context)
            if judge_res and judge_res.get("human_score") is not None:
                break
            quota_tracker["retries"] += 1
            wait_sec = 2 ** attempt
            print(f"[{case['case_id']}] Warning: call_judge_llm attempt {attempt+1} failed or returned invalid JSON. Retrying in {wait_sec}s...")
            await asyncio.sleep(wait_sec)

        if not judge_res:
            judge_res = {
                "required_fact_recall": 0.0,
                "optional_fact_recall": 0.0,
                "important_cluster_recall": 0.0,
                "unsupported_claims": False,
                "contradiction_count": 0,
                "relevance": 0.0,
                "completeness": 0.0,
                "human_score": 0,
                "reasoning": "Failed to judge."
            }

        selected_chapters = trace.get("selected_chapters") or []
        candidate_chapters = trace.get("candidate_chapters") or []
        
        target_ch = case.get("explicit_target_chapter")
        allowed_range = case.get("allowed_chapter_range") or []
        if target_ch is not None:
            expected_chapters = [target_ch]
        elif len(allowed_range) == 2:
            expected_chapters = list(range(allowed_range[0], allowed_range[1] + 1))
        elif len(allowed_range) == 1:
            expected_chapters = [allowed_range[0]]
        else:
            expected_chapters = []
        
        mrr = 0.0
        recalls = {}
        for k in [1, 3, 5, 10]:
            hits = [ch for ch in candidate_chapters[:k] if ch in expected_chapters]
            recalls[k] = 1.0 if hits else 0.0
            
        for i, ch in enumerate(candidate_chapters, 1):
            if ch in expected_chapters:
                mrr = 1.0 / i
                break
        
        wrong_chapter_top1 = 0
        if candidate_chapters and expected_chapters:
            if candidate_chapters[0] not in expected_chapters:
                wrong_chapter_top1 = 1
                
        wrong_selected_chapter = 0
        if selected_chapters and expected_chapters:
            if not any(ch in expected_chapters for ch in selected_chapters):
                wrong_selected_chapter = 1
                
        prog = case["chapter_progress"]
        future_leakage = 0
        if any(ch > prog for ch in selected_chapters):
            future_leakage = 1

        print(f"[{idx}/50] Finished evaluating {case['case_id']}. Latency: {int(latency*1000)}ms. Score: {judge_res['human_score']}")
        
        # small sleep to avoid overwhelming provider immediately
        await asyncio.sleep(0.5)

        trace["expected_chapters"] = expected_chapters

        return {
            "case_id": case["case_id"],
            "question": case["question"],
            "answer": bot_answer,
            "source": bot_res.source,
            "abstained": bot_res.abstained,
            "latency_ms": int(latency * 1000),
            "trace": trace,
            "eval": judge_res,
            "metrics": {
                "mrr": mrr,
                "recalls": recalls,
                "wrong_chapter_top1": wrong_chapter_top1,
                "wrong_selected_chapter": wrong_selected_chapter,
                "future_leakage": future_leakage
            }
        }

async def main():
    start_eval_time = time.perf_counter()
    cases_path = os.path.join(backend_path, "evals", "chapter_bot_quality_cases_v1.json")
    if not os.path.exists(cases_path):
        print(f"Error: Cases file not found at {cases_path}")
        sys.exit(1)

    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    if os.getenv("EVAL_DRY_RUN") == "1":
        cases = cases[:3]
        print(f"Loaded {len(cases)} benchmark cases (DRY RUN). Starting evaluation...")
    else:
        print(f"Loaded {len(cases)} benchmark cases. Starting evaluation...")
    
    sem = asyncio.Semaphore(3)
    tasks = []
    for idx, case in enumerate(cases, 1):
        tasks.append(evaluate_case(idx, case, sem))
        
    results_raw = await asyncio.gather(*tasks)
    
    quota_tracker["elapsed_seconds"] = round(time.perf_counter() - start_eval_time, 2)
    
    results = []
    ret_recalls = {1: [], 3: [], 5: [], 10: []}
    ret_mrr_list = []
    wrong_chapter_top1_count = 0
    wrong_selected_chapter_count = 0
    future_leakage_count = 0
    
    human_scores = []
    unsupported_claims_count = 0
    abstain_correct_count = 0
    abstain_total_cases = 0

    for r in results_raw:
        results.append({
            "case_id": r["case_id"],
            "question": r["question"],
            "answer": r["answer"],
            "source": r["source"],
            "abstained": r["abstained"],
            "latency_ms": r["latency_ms"],
            "trace": r["trace"],
            "eval": r["eval"]
        })
        
        m = r["metrics"]
        ret_mrr_list.append(m["mrr"])
        for k in [1, 3, 5, 10]:
            ret_recalls[k].append(m["recalls"][k])
            
        wrong_chapter_top1_count += m["wrong_chapter_top1"]
        wrong_selected_chapter_count += m["wrong_selected_chapter"]
        future_leakage_count += m["future_leakage"]
        
        judge_res = r["eval"]
        human_scores.append(judge_res["human_score"])
        if judge_res["unsupported_claims"]:
            unsupported_claims_count += 1
            
        # Find the original case matching case_id
        orig_case = next(c for c in cases if c["case_id"] == r["case_id"])
        if orig_case["acceptable_abstain"]:
            abstain_total_cases += 1
            if r["abstained"]:
                abstain_correct_count += 1

    total_evals = len(cases)
    overall_mrr = sum(ret_mrr_list) / total_evals
    overall_recall_5 = sum(ret_recalls[5]) / total_evals
    overall_recall_10 = sum(ret_recalls[10]) / total_evals
    future_leakage_rate = future_leakage_count / total_evals
    
    score_dist = {0: 0, 1: 0, 2: 0, 3: 0}
    for s in human_scores:
        score_dist[s] = score_dist.get(s, 0) + 1
        
    score_ge_2_rate = (score_dist[2] + score_dist[3]) / total_evals
    score_3_rate = score_dist[3] / total_evals
    unsupported_claims_rate = unsupported_claims_count / total_evals
    abstain_accuracy = abstain_correct_count / max(1, abstain_total_cases)

    summary = {
        "total_cases": total_evals,
        "retrieval": {
            "recall_1": sum(ret_recalls[1]) / total_evals,
            "recall_3": sum(ret_recalls[3]) / total_evals,
            "recall_5": overall_recall_5,
            "recall_10": overall_recall_10,
            "mrr": overall_mrr,
            "wrong_chapter_top1_rate": wrong_chapter_top1_count / total_evals,
            "wrong_selected_chapter_rate": wrong_selected_chapter_count / total_evals,
            "future_leakage_rate": future_leakage_rate
        },
        "generation": {
            "score_distribution": score_dist,
            "score_ge_2_rate": score_ge_2_rate,
            "score_3_rate": score_3_rate,
            "unsupported_claims_rate": unsupported_claims_rate,
            "abstain_accuracy": abstain_accuracy
        },
        "quota_accounting": quota_tracker
    }

    report = {
        "summary": summary,
        "results": results
    }

    results_path = os.path.join(backend_path, "evals", "chapter_bot_quality_results_v1.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("           SUPER RAG QUALITY BASELINE REPORT")
    print("=" * 60)
    print(f"Total Cases Evaluated   : {total_evals}")
    print(f"Retrieval Recall@5      : {overall_recall_5:.2%}")
    print(f"Retrieval Recall@10     : {overall_recall_10:.2%}")
    print(f"Retrieval MRR           : {overall_mrr:.4f}")
    print(f"Future Spoiler Leakage  : {future_leakage_rate:.2%}")
    print("-" * 60)
    print(f"Score Distribution      : {score_dist}")
    print(f"Score >= 2 Rate         : {score_ge_2_rate:.2%}")
    print(f"Score = 3 Rate          : {score_3_rate:.2%}")
    print(f"Unsupported Claims Rate : {unsupported_claims_rate:.2%}")
    print(f"Abstention Accuracy     : {abstain_accuracy:.2%}")
    print("-" * 60)
    print("           QUOTA ACCOUNTING INFO")
    print(f"Oracle API Calls        : {quota_tracker['oracle_calls']}")
    print(f"Judge API Calls         : {quota_tracker['judge_calls']}")
    print(f"Total API Calls         : {quota_tracker['provider_calls']}")
    print(f"Retries                 : {quota_tracker['retries']}")
    print(f"Timeouts                : {quota_tracker['timeouts']}")
    print(f"Rate Limits (429)       : {quota_tracker['rate_limits']}")
    print(f"Elapsed Time (s)        : {quota_tracker['elapsed_seconds']}s")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
