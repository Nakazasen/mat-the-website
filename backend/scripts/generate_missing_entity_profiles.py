import os
import sys
import argparse
import json

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

from backend.rag.retrieval import search_story_chunks_hybrid_lexical
from backend.rag.missing_entity_analysis import extract_missing_entities_from_failure_report, normalize_entity_name

def print_safe(text):
    """Safely print text on Windows consoles to prevent encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='backslashreplace').decode('ascii'))

def guess_entity_type(name: str, evidence: list) -> str:
    """Guesses the entity type based on name and evidence keywords matching Phase 5S schema."""
    name_lower = name.lower()
    combined_text = (name_lower + " " + " ".join([e.get("preview", "") for e in evidence])).lower()
    
    # character check
    if any(kw in name_lower for kw in ["nhân vật", "giám đốc", "lâm nhã vy", "trương hạo", "vương mạnh", "lý đức", "bàng lâm", "sếp", "phong", "vy", "hạo", "mạnh", "đức", "lâm", "chủ tịch"]):
        return "character"
    if any(kw in combined_text for kw in ["hắn", "nàng", "anh ta", "cô ta", "nhân vật"]):
        return "character"
        
    # faction check
    if any(kw in name_lower for kw in ["công ty", "tổ chức", "thế lực", "quân đội", "bang hội", "đại thiên thần", "phòng điều hành"]):
        return "faction"
    if any(kw in combined_text for kw in ["công ty", "tổ chức", "thế lực", "quân đội", "bang"]):
        return "faction"
        
    # item check
    if any(kw in name_lower for kw in ["vật phẩm", "trang bị", "vũ khí", "dịch thể", "hộp thực phẩm", "tinh thể", "thẻ triệu hồi"]):
        return "item"
    if any(kw in combined_text for kw in ["vật phẩm", "trang bị", "vũ khí", "tinh thể", "dịch thể"]):
        return "item"
        
    # location check
    if any(kw in name_lower for kw in ["tòa nhà", "căng tin", "phòng điện", "nhà kho", "tầng hầm", "khu vực", "địa điểm", "thành phố"]):
        return "location"
    if any(kw in combined_text for kw in ["tòa nhà", "căng tin", "phòng điện", "nhà kho", "tầng hầm", "khu vực", "thành phố"]):
        return "location"
        
    # concept check
    if any(kw in name_lower for kw in ["dị năng", "kỹ năng", "chiêu thức", "băng thứ", "băng giáp", "thăng cấp", "tác dụng", "hệ thống", "sinh tồn"]):
        return "concept"
    if any(kw in combined_text for kw in ["dị năng", "kỹ năng", "chiêu thức", "hệ thống"]):
        return "concept"
        
    return "unknown"

def build_missing_profile_drafts(missing_entities: list[dict], chapter_cap: int, supabase_client) -> list[dict]:
    """Search story chunks for each missing entity and generate profile drafts."""
    drafts = []
    
    for ent_info in missing_entities:
        name = ent_info["entity_name"]
        priority = ent_info["priority"]
        
        results = []
        if supabase_client:
            try:
                results = search_story_chunks_hybrid_lexical(
                    supabase=supabase_client,
                    query=name,
                    chapter_cap=chapter_cap,
                    limit=5
                )
            except Exception as e:
                print_safe(f"Warning: search failed for {name}: {e}")
                
        evidence_list = []
        for r in results:
            content = r.get("content_plain") or r.get("content") or ""
            preview = r.get("content_preview") or (content[:200] + "..." if len(content) > 200 else content)
            
            evidence_list.append({
                "chapter_number": r.get("chapter_number"),
                "chapter_title": r.get("chapter_title"),
                "chunk_index": r.get("chunk_index"),
                "content_hash": r.get("content_hash"),
                "preview": preview
            })
            
        guessed_type = guess_entity_type(name, evidence_list)
        status = "draft" if len(evidence_list) > 0 else "needs_review"
        
        drafts.append({
            "entity_name": name,
            "entity_type": guessed_type,
            "summary": "",
            "content": "",
            "status": status,
            "priority": priority,
            "evidence": evidence_list,
            "source": "missing_entity_failure_report",
            "human_review_required": True
        })
        
    return drafts

def main():
    parser = argparse.ArgumentParser(description="Generate profile drafts for missing entities.")
    parser.add_argument("--failure-report", type=str, default="backend/rag/generated_all_failure_report_after_5q.json", help="Path to evaluator failure report JSON.")
    parser.add_argument("--chapter-cap", type=int, default=829, help="Max chapter number limit for evidence.")
    parser.add_argument("--limit-entities", type=int, default=50, help="Max number of missing entities to process.")
    parser.add_argument("--output", type=str, default="backend/rag/generated_missing_entity_profiles.json", help="Output path for profile drafts JSON.")
    
    args = parser.parse_args()
    
    # Read failure report
    report_path = os.path.abspath(args.failure_report)
    if not os.path.exists(report_path):
        print_safe(f"Error: Failure report not found at {report_path}")
        sys.exit(1)
        
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    except Exception as e:
        print_safe(f"Error reading failure report: {e}")
        sys.exit(1)
        
    # Extract entities
    missing_entities = extract_missing_entities_from_failure_report(report)
    print_safe(f"Total missing entities extracted from report: {len(missing_entities)}")
    
    # Limit entities
    if args.limit_entities:
        missing_entities = missing_entities[:args.limit_entities]
        print_safe(f"Limiting processing to top {len(missing_entities)} entities.")
        
    # Build drafts
    print_safe(f"Running hybrid lexical search in story_chunks up to chapter {args.chapter_cap}...")
    drafts = build_missing_profile_drafts(missing_entities, args.chapter_cap, supabase)
    
    # Stats
    drafts_with_evidence = sum(1 for d in drafts if d["status"] == "draft")
    drafts_needs_review = len(drafts) - drafts_with_evidence
    
    print_safe("-" * 60)
    print_safe("TOP 10 MISSING ENTITIES RANKED:")
    for i, ent in enumerate(missing_entities[:10]):
        print_safe(f"{i+1}. {ent['entity_name']} (count: {ent['count']}, priority: {ent['priority']})")
    print_safe("-" * 60)
    print_safe(f"Generated drafts: {len(drafts)}")
    print_safe(f"Drafts with evidence: {drafts_with_evidence}")
    print_safe(f"Drafts needing human review (no evidence): {drafts_needs_review}")
    
    # Save output
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(drafts, f, indent=2, ensure_ascii=False)
        print_safe(f"Draft profiles saved to: {output_path}")
    except Exception as e:
        print_safe(f"Error saving drafts to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
