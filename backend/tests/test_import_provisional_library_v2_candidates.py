import pytest
import json
from unittest.mock import MagicMock, patch
from backend.scripts.import_provisional_library_v2_candidates import build_db_payload

def test_build_db_payload_v2():
    record = {
        "id": "mock_v2_id",
        "name": "Tinh Thạch Khai Phá",
        "normalized_name": "Tinh Thạch Khai Phá",
        "type": "crystal_core",
        "summary": "Tinh thạch đặc biệt.",
        "evidence": [
            {"chapter_number": 5, "preview": "ev1"},
            {"chapter_number": 10, "preview": "ev2"},
            {"chapter_number": 5, "preview": "ev3"}
        ],
        "confidence": 0.95,
        "quality_class": "high_confidence"
    }
    
    payload = build_db_payload(record, source_value="story_chunks_auto_extract_v2")
    
    assert payload["id"] == "mock_v2_id"
    assert payload["name"] == "Tinh Thạch Khai Phá"
    assert payload["normalized_name"] == "Tinh Thạch Khai Phá"
    assert payload["type"] == "crystal_core"
    assert payload["summary"] == "Tinh thạch đặc biệt."
    assert payload["confidence"] == 0.95
    assert payload["quality_class"] == "high_confidence"
    assert payload["source"] == "story_chunks_auto_extract_v2"
    assert payload["chapter_numbers"] == [5, 10]
    assert payload["first_chapter"] == 5
    assert payload["last_chapter"] == 10

@patch("backend.scripts.import_provisional_library_v2_candidates.supabase")
def test_import_script_dry_run(mock_supabase):
    # Just running main with arguments
    from backend.scripts.import_provisional_library_v2_candidates import main
    
    # Mocking command line arguments
    test_args = ["--input", "backend/tests/test_entity_drafts.py", "--dry-run"]
    
    with patch("sys.argv", ["import_provisional_library_v2_candidates.py"] + test_args), \
         patch("json.load", return_value=[{"id": "1", "name": "Test Item"}]):
        # Should execute successfully without calling Supabase because it is a dry-run
        main()
        mock_supabase.table.assert_not_called()
