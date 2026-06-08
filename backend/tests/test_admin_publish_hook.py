import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

try:
    import main
    from main import app
except ImportError:
    import backend.main as main
    from backend.main import app

client = TestClient(app)


def test_publish_valid_chapter(monkeypatch):
    # Mock admin authentication
    async def fake_verify_admin(_authorization):
        return {"id": "admin-id", "email": "admin@example.com", "role": "admin"}
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    # Mock R2 client
    mock_r2 = MagicMock()
    monkeypatch.setattr(main, "r2_client", mock_r2)

    # Mock Supabase
    mock_supabase = MagicMock()
    monkeypatch.setattr(main, "supabase", mock_supabase)

    # Mock current last chapter number to 829
    # Chain: supabase.table("story_chunks").select("chapter_number").order().limit().execute()
    mock_chunks_res = MagicMock()
    mock_chunks_res.data = [{"chapter_number": 829}]
    
    mock_table = mock_supabase.table
    mock_select = mock_table.return_value.select
    mock_order = mock_select.return_value.order
    mock_limit = mock_order.return_value.limit
    mock_limit.return_value.execute.return_value = mock_chunks_res

    # Mock insert responses
    mock_chapter_res = MagicMock()
    mock_chapter_res.data = [{"id": "chapter-uuid-830", "chapter_number": 830, "title": "Chương 830: Khởi Đầu Mới"}]
    
    mock_insert = mock_table.return_value.insert
    # Set return value for chapters insertion
    mock_insert.return_value.execute.side_effect = [
        MagicMock(data=[{"id": "staging-uuid-1"}]), # Staging log insert
        mock_chapter_res,                           # Chapter insert
        MagicMock(data=[{"id": "chunk-uuid-1"}])     # Chunks insert
    ]

    # Mock unique check (uniqueness in chapters table check)
    # Chain: supabase.table("chapters").select("id").eq("chapter_number", 830).execute()
    mock_eq_res = MagicMock()
    mock_eq_res.data = [] # No existing duplicate
    mock_table.return_value.select.return_value.eq.return_value.execute.return_value = mock_eq_res

    # Mock oracle_cache select/delete
    # Chain: supabase.table("oracle_cache").select().gte().execute()
    mock_oracle_cache_res = MagicMock()
    mock_oracle_cache_res.data = []
    mock_table.return_value.select.return_value.gte.return_value.execute.return_value = mock_oracle_cache_res

    payload = {
        "chapter_number": 830,
        "title": "Chương 830: Khởi Đầu Mới",
        "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        "is_side_story": False
    }

    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/api/admin/chapters", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Thêm chương thành công"
    assert data["chapter"]["chapter_number"] == 830

    # Ensure R2 was called
    assert mock_r2.put_object.call_count == 1
    # Ensure chapters insert was called
    mock_table.assert_any_call("chapters")
    # Ensure story_chunks insert was called
    mock_table.assert_any_call("story_chunks")


def test_publish_invalid_historical(monkeypatch):
    # Mock admin authentication
    async def fake_verify_admin(_authorization):
        return {"id": "admin-id", "email": "admin@example.com", "role": "admin"}
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    # Mock R2 client
    mock_r2 = MagicMock()
    monkeypatch.setattr(main, "r2_client", mock_r2)

    # Mock Supabase
    mock_supabase = MagicMock()
    monkeypatch.setattr(main, "supabase", mock_supabase)

    # Mock current last chapter number to 829
    mock_chunks_res = MagicMock()
    mock_chunks_res.data = [{"chapter_number": 829}]
    
    mock_table = mock_supabase.table
    mock_select = mock_table.return_value.select
    mock_order = mock_select.return_value.order
    mock_limit = mock_order.return_value.limit
    mock_limit.return_value.execute.return_value = mock_chunks_res

    # Mock staging insert
    mock_table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "staging-uuid-1"}])

    payload = {
        "chapter_number": 820, # Historical chapter <= 829
        "title": "Chương 820: Trùng lịch sử",
        "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        "is_side_story": False
    }

    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/api/admin/chapters", json=payload, headers=headers)

    assert response.status_code == 400
    assert "historical data is blocked" in response.json()["detail"].lower()

    # R2 and chapters should NOT be written
    assert mock_r2.put_object.call_count == 0
    # chapters table should not be inserted
    # It might be selected for last_chapter/uniqueness, but not inserted.
    # We can check insert call count
    mock_table.return_value.insert.assert_called_once() # Called only once for new_chapter_staging


def test_publish_invalid_sequence_gap(monkeypatch):
    # Mock admin authentication
    async def fake_verify_admin(_authorization):
        return {"id": "admin-id", "email": "admin@example.com", "role": "admin"}
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    # Mock Supabase
    mock_supabase = MagicMock()
    monkeypatch.setattr(main, "supabase", mock_supabase)

    # Mock current last chapter number to 829
    mock_chunks_res = MagicMock()
    mock_chunks_res.data = [{"chapter_number": 829}]
    mock_table = mock_supabase.table
    mock_table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_chunks_res
    mock_table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    payload = {
        "chapter_number": 832, # Gap 830 and 831
        "title": "Chương 832: Gaps",
        "content": "Nội dung chương truyện Diệp Phàm tiếp tục đi tìm các tinh thể zombie cấp cao ở thành phố hoang tàn.",
        "is_side_story": False
    }

    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/api/admin/chapters", json=payload, headers=headers)

    assert response.status_code == 400
    assert "sequence gap detected" in response.json()["detail"].lower()


def test_publish_invalid_content_too_short(monkeypatch):
    # Mock admin authentication
    async def fake_verify_admin(_authorization):
        return {"id": "admin-id", "email": "admin@example.com", "role": "admin"}
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    # Mock Supabase
    mock_supabase = MagicMock()
    monkeypatch.setattr(main, "supabase", mock_supabase)

    # Mock current last chapter number to 829
    mock_chunks_res = MagicMock()
    mock_chunks_res.data = [{"chapter_number": 829}]
    mock_table = mock_supabase.table
    mock_table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_chunks_res
    mock_table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    payload = {
        "chapter_number": 830,
        "title": "Chương 830: Quá ngắn",
        "content": "", # Empty content
        "is_side_story": False
    }

    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/api/admin/chapters", json=payload, headers=headers)

    assert response.status_code == 400
    assert "completely empty" in response.json()["detail"].lower()


def test_publish_invalid_html_tags(monkeypatch):
    # Mock admin authentication
    async def fake_verify_admin(_authorization):
        return {"id": "admin-id", "email": "admin@example.com", "role": "admin"}
    monkeypatch.setattr(main, "verify_admin", fake_verify_admin)

    # Mock Supabase
    mock_supabase = MagicMock()
    monkeypatch.setattr(main, "supabase", mock_supabase)

    # Mock current last chapter number to 829
    mock_chunks_res = MagicMock()
    mock_chunks_res.data = [{"chapter_number": 829}]
    mock_table = mock_supabase.table
    mock_table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_chunks_res
    mock_table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    payload = {
        "chapter_number": 830,
        "title": "Chương 830: HTML",
        "content": "<p>Nội dung chứa thẻ</p> <script>alert(1)</script>",
        "is_side_story": False
    }

    headers = {"Authorization": "Bearer fake-token"}
    response = client.post("/api/admin/chapters", json=payload, headers=headers)

    assert response.status_code == 400
    assert "html tags or script elements" in response.json()["detail"].lower()
