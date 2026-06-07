import pytest
from unittest.mock import MagicMock, patch
from backend.scripts.restore_provisional_library_backup import perform_restore

class MockTable:
    def __init__(self, name):
        self.name = name
        self.delete_called = False
        self.insert_called = False
        self.inserted_payloads = []
        
    def delete(self):
        self.delete_called = True
        return self
        
    def neq(self, field, value):
        return self
        
    def insert(self, payloads):
        self.insert_called = True
        self.inserted_payloads.extend(payloads)
        return self
        
    def execute(self):
        class MockResponse:
            def __init__(self):
                self.data = [{"id": "deleted_id"}]
        return MockResponse()

class MockSupabase:
    def __init__(self):
        self.tables = {}
        
    def table(self, table_name):
        if table_name not in self.tables:
            self.tables[table_name] = MockTable(table_name)
        return self.tables[table_name]

@patch("backend.scripts.restore_provisional_library_backup.supabase")
def test_perform_restore_dry_run(mock_supabase):
    mock_file_content = [{"id": "1", "name": "Hàn Phong", "type": "character"}]
    
    with patch("json.load", return_value=mock_file_content), \
         patch("builtins.open", MagicMock()):
        summary = perform_restore("mock_path.json", dry_run=True)
        
        assert summary["read_count"] == 1
        assert summary["inserted_count"] == 1
        assert summary["deleted_count"] == 0
        mock_supabase.table.assert_not_called()

def test_perform_restore_write():
    mock_file_content = [{
        "id": "1",
        "name": "Hàn Phong",
        "type": "character",
        "evidence": [{"chapter_number": 1}]
    }]
    
    mock_client = MockSupabase()
    
    with patch("backend.scripts.restore_provisional_library_backup.supabase", mock_client), \
         patch("json.load", return_value=mock_file_content), \
         patch("builtins.open", MagicMock()):
        summary = perform_restore("mock_path.json", dry_run=False)
        
        assert summary["read_count"] == 1
        assert summary["inserted_count"] == 1
        assert summary["deleted_count"] == 1
        
        table = mock_client.table("provisional_library")
        assert table.delete_called is True
        assert table.insert_called is True
        assert len(table.inserted_payloads) == 1
        assert table.inserted_payloads[0]["id"] == "1"
        assert table.inserted_payloads[0]["name"] == "Hàn Phong"
