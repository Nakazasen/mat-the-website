import json
from unittest.mock import MagicMock, patch
from backend.rag.missing_entity_analysis import (
    normalize_entity_name,
    rank_missing_entities,
    extract_missing_entities_from_failure_report
)
from backend.scripts.generate_missing_entity_profiles import (
    guess_entity_type,
    build_missing_profile_drafts
)

def test_normalize_entity_name():
    assert normalize_entity_name("  Tinh  thể   zombie  ") == "Tinh thể zombie"
    assert normalize_entity_name("\nLâm  Nhã   Vy\n") == "Lâm Nhã Vy"
    assert normalize_entity_name("") == ""
    assert normalize_entity_name(None) == ""

def test_rank_missing_entities_priority():
    mock_entities = [
        {"entity_name": "Entity A", "count": 1},
        {"entity_name": "Entity B", "count": 3},
        {"entity_name": "Entity C", "count": 2}
    ]
    ranked = rank_missing_entities(mock_entities)
    
    assert len(ranked) == 3
    # Verify count sorting (descending)
    assert ranked[0]["entity_name"] == "Entity B"
    assert ranked[0]["priority"] == "high"
    
    assert ranked[1]["entity_name"] == "Entity C"
    assert ranked[1]["priority"] == "medium"
    
    assert ranked[2]["entity_name"] == "Entity A"
    assert ranked[2]["priority"] == "low"

def test_extract_missing_entities_from_detailed_report():
    mock_report = {
        "results": [
            {
                "id": "case-1",
                "intent": "identity",
                "entity_name": "Lâm Nhã Vy",
                "missing_entity_context": True,
                "passed": False,
                "question": "Lâm Nhã Vy là ai?"
            },
            {
                "id": "case-2",
                "intent": "identity",
                "entity_name": "Lâm Nhã Vy",
                "missing_entity_context": True,
                "passed": False,
                "question": "Thân thế Lâm Nhã Vy?"
            },
            {
                "id": "case-3",
                "intent": "identity",
                "entity_name": "Trương Hạo",
                "missing_entity_context": True,
                "passed": False,
                "question": "Trương Hạo là ai?"
            }
        ]
    }
    extracted = extract_missing_entities_from_failure_report(mock_report)
    
    assert len(extracted) == 2
    assert extracted[0]["entity_name"] == "Lâm Nhã Vy"
    assert extracted[0]["count"] == 2
    assert "identity" in extracted[0]["intents"]
    assert "case-1" in extracted[0]["case_ids"]
    assert "Lâm Nhã Vy là ai?" in extracted[0]["questions"]
    
    assert extracted[1]["entity_name"] == "Trương Hạo"
    assert extracted[1]["count"] == 1

def test_extract_missing_entities_from_summary_report():
    mock_report = {
        "top_missing_entities": [
            {"entity": "Vương Mạnh", "count": 3},
            {"entity": "Lý Đức", "count": 1}
        ]
    }
    extracted = extract_missing_entities_from_failure_report(mock_report)
    
    assert len(extracted) == 2
    assert extracted[0]["entity_name"] == "Vương Mạnh"
    assert extracted[0]["count"] == 3
    assert extracted[0]["priority"] == "high"
    
    assert extracted[1]["entity_name"] == "Lý Đức"
    assert extracted[1]["count"] == 1
    assert extracted[1]["priority"] == "low"

def test_guess_entity_type_heuristics():
    # Character check
    assert guess_entity_type("Lâm Nhã Vy", []) == "character"
    assert guess_entity_type("Chủ tịch công ty", [{"preview": "Hắn gật đầu với tôi."}]) == "character"
    
    # Faction check
    assert guess_entity_type("Đại Thiên Thần", []) == "faction"
    assert guess_entity_type("Tập đoàn Đại Thiên", [{"preview": "Thế lực này rất mạnh."}]) == "faction"
    
    # Item check
    assert guess_entity_type("Tinh thể zombie cấp 2", []) == "item"
    assert guess_entity_type("Dịch thể", [{"preview": "Vật phẩm rơi ra khi giết quái."}]) == "item"
    
    # Location check
    assert guess_entity_type("Sảnh căng tin", []) == "location"
    assert guess_entity_type("Nhà kho tầng hầm", [{"preview": "Chúng tôi chạy trốn vào nhà kho."}]) == "location"
    
    # Concept check
    assert guess_entity_type("Dị năng giả hệ băng", []) == "concept"
    
    # Unknown check
    assert guess_entity_type("Một khái niệm lạ", []) == "unknown"

def test_build_profile_drafts_with_evidence():
    mock_supabase = MagicMock()
    mock_missing = [
        {"entity_name": "Lâm Nhã Vy", "count": 2, "priority": "medium"}
    ]
    
    mock_search_result = [
        {
            "chapter_number": 1,
            "chapter_title": "Chương 1: Mạt thế",
            "chunk_index": 3,
            "content_plain": "Lâm Nhã Vy là đồng nghiệp của Hàn Phong.",
            "content_hash": "hash123"
        }
    ]
    
    with patch("backend.scripts.generate_missing_entity_profiles.search_story_chunks_hybrid_lexical", return_value=mock_search_result) as mock_search:
        drafts = build_missing_profile_drafts(mock_missing, chapter_cap=829, supabase_client=mock_supabase)
        
        mock_search.assert_called_once()
        assert len(drafts) == 1
        
        d = drafts[0]
        assert d["entity_name"] == "Lâm Nhã Vy"
        assert d["entity_type"] == "character"
        assert d["status"] == "draft" # status is "draft" because we have evidence
        assert d["priority"] == "medium"
        assert d["summary"] == ""
        assert d["content"] == ""
        assert d["source"] == "missing_entity_failure_report"
        assert d["human_review_required"] is True
        
        # Verify evidence mapping
        assert len(d["evidence"]) == 1
        ev = d["evidence"][0]
        assert ev["chapter_number"] == 1
        assert ev["chapter_title"] == "Chương 1: Mạt thế"
        assert ev["chunk_index"] == 3
        assert ev["content_hash"] == "hash123"
        assert ev["preview"] == "Lâm Nhã Vy là đồng nghiệp của Hàn Phong."

def test_build_profile_drafts_without_evidence():
    mock_supabase = MagicMock()
    mock_missing = [
        {"entity_name": "Không có thật", "count": 1, "priority": "low"}
    ]
    
    with patch("backend.scripts.generate_missing_entity_profiles.search_story_chunks_hybrid_lexical", return_value=[]) as mock_search:
        drafts = build_missing_profile_drafts(mock_missing, chapter_cap=829, supabase_client=mock_supabase)
        
        assert len(drafts) == 1
        d = drafts[0]
        assert d["entity_name"] == "Không có thật"
        assert d["status"] == "needs_review" # needs_review when evidence is empty
        assert d["evidence"] == []
        
        # Verify no database mutation calls on mock_supabase
        assert mock_supabase.table.called is False

def test_json_serializable():
    mock_draft = {
        "entity_name": "Trương Hạo",
        "entity_type": "character",
        "summary": "",
        "content": "",
        "status": "draft",
        "priority": "low",
        "evidence": [
            {
                "chapter_number": 2,
                "chapter_title": "Chương 2",
                "chunk_index": 0,
                "content_hash": "hash456",
                "preview": "Trương Hạo gật đầu."
            }
        ],
        "source": "missing_entity_failure_report",
        "human_review_required": True
    }
    # Verify serializing works
    json_str = json.dumps(mock_draft)
    parsed = json.loads(json_str)
    assert parsed["entity_name"] == "Trương Hạo"
    assert parsed["evidence"][0]["chapter_number"] == 2
