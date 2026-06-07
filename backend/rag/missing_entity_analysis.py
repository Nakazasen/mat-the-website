import re

def normalize_entity_name(name: str) -> str:
    """Standardizes entity name by removing leading/trailing spaces and collapsing whitespace."""
    if not name:
        return ""
    return re.sub(r"\s+", " ", name.strip())

def rank_missing_entities(entities: list[dict]) -> list[dict]:
    """
    Ranks the list of missing entities by count descending,
    and assigns priority ('high', 'medium', 'low') based on count.
    """
    # Sort by count descending, then by name alphabetically
    sorted_entities = sorted(entities, key=lambda x: (-x.get("count", 0), x.get("entity_name", "")))
    
    for item in sorted_entities:
        count = item.get("count", 0)
        if count >= 3:
            item["priority"] = "high"
        elif count == 2:
            item["priority"] = "medium"
        else:
            item["priority"] = "low"
            
    return sorted_entities

def extract_missing_entities_from_failure_report(report: dict) -> list[dict]:
    """
    Extracts missing entities from either a detailed evaluator report (containing 'results')
    or a summary failure report (containing 'top_missing_entities').
    """
    if not report:
        return []

    entities_map = {}

    # Format B: Detailed evaluator report containing results list
    if "results" in report:
        for res in report.get("results", []):
            if res.get("missing_entity_context") and res.get("entity_name"):
                name = normalize_entity_name(res["entity_name"])
                if not name:
                    continue
                
                case_id = res.get("id")
                question = res.get("question") or ""
                intent = res.get("intent") or "unknown"
                
                if name not in entities_map:
                    entities_map[name] = {
                        "entity_name": name,
                        "count": 0,
                        "intents": set(),
                        "case_ids": set(),
                        "questions": set(),
                        "priority": "low"
                    }
                
                entities_map[name]["count"] += 1
                if intent:
                    entities_map[name]["intents"].add(intent)
                if case_id:
                    entities_map[name]["case_ids"].add(case_id)
                if question:
                    entities_map[name]["questions"].add(question)

        # Convert sets to sorted lists for JSON serializability
        entities_list = []
        for name, data in entities_map.items():
            data["intents"] = sorted(list(data["intents"]))
            data["case_ids"] = sorted(list(data["case_ids"]))
            data["questions"] = sorted(list(data["questions"]))
            entities_list.append(data)
        
        return rank_missing_entities(entities_list)

    # Format A: Summary report containing top_missing_entities
    elif "top_missing_entities" in report:
        for item in report.get("top_missing_entities", []):
            raw_name = item.get("entity") or item.get("entity_name")
            if not raw_name:
                continue
            name = normalize_entity_name(raw_name)
            count = item.get("count", 1)
            
            if name not in entities_map:
                entities_map[name] = {
                    "entity_name": name,
                    "count": count,
                    "intents": [],
                    "case_ids": [],
                    "questions": [],
                    "priority": "low"
                }
            else:
                entities_map[name]["count"] += count

        entities_list = list(entities_map.values())
        return rank_missing_entities(entities_list)

    return []
