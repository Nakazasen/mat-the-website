import pytest
from unittest.mock import MagicMock, patch
from backend.rag.oracle_feedback_classifier import classify_oracle_feedback
from backend.rag.oracle_answer_patch_builder import build_oracle_patches
from backend.scripts.run_oracle_answer_feedback_pipeline import run_pipeline

# 1. Test Classification Heuristics
def test_classification_heuristics():
    # Test shallow answer complaint
    res_shallow = classify_oracle_feedback(
        question="Hạ Huyền Sương là ai?",
        answer="Hạ Huyền Sương là một nhân vật nữ.",
        user_feedback="Câu trả lời về nhân vật quá máy móc và sơ sài"
    )
    assert res_shallow["issue_type"] == "answer_quality_too_shallow"
    assert res_shallow["suggested_policy_type"] == "enrich_identity_answer_from_story_chunks"
    assert res_shallow["target_entity_or_intent"] == "Hạ Huyền Sương"

    # Test intent misclassification
    res_intent = classify_oracle_feedback(
        question="Nội dung chương truyện là gì?",
        answer="Hàn Phong (nhân vật), Căn cứ Hi Vọng (tổ chức).",
        user_feedback="Người dùng đang hỏi về tóm tắt nội dung chương truyện lại đi trả lời linh tinh về tổ chức/nhân vật"
    )
    assert res_intent["issue_type"] == "intent_misclassification"
    assert res_intent["suggested_policy_type"] == "prefer_chapter_summary_intent"
    assert res_intent["target_entity_or_intent"] == "chapter_summary"

    # Test irrelevant entities complaint
    res_irrelevant = classify_oracle_feedback(
        question="Tinh thể zombie là gì?",
        answer="Tinh thể zombie là vật phẩm. Ngoài ra còn có Hàn Phong là người sở hữu.",
        user_feedback="Đưa thêm thông tin lan man không liên quan"
    )
    assert res_irrelevant["issue_type"] == "irrelevant_entities"
    assert res_irrelevant["suggested_policy_type"] == "suppress_irrelevant_entity_expansion"

    # Test missing exact entity
    res_missing = classify_oracle_feedback(
        question="Súng Diệt Quỷ là gì?",
        answer="[CHƯA CÓ MỤC ĐỊNH DANH CHÍNH XÁC] Chưa tìm thấy mục chính xác.",
        user_feedback="Thiếu thông tin vật phẩm này"
    )
    assert res_missing["issue_type"] == "missing_exact_entity"
    assert res_missing["suggested_policy_type"] == "force_exact_entity_lookup"


# 2. Test Patch Builder
def test_patch_builder():
    feedbacks = [
        {
            "id": "fb-1",
            "question": "Hạ Huyền Sương là ai?",
            "answer": "Hạ Huyền Sương là một nhân vật nữ.",
            "user_comment": "Câu trả lời về nhân vật quá máy móc và sơ sài",
            "source": "ai_provider",
            "status": "pending"
        },
        {
            "id": "fb-2",
            "question": "nội dung chương truyện là gì?",
            "answer": "Hàn Phong (nhân vật), Căn cứ Hi Vọng (tổ chức).",
            "user_comment": "Hỏi tóm tắt chương nhưng trả linh tinh tổ chức/nhân vật",
            "source": "local_wiki",
            "status": "pending"
        }
    ]

    patches = build_oracle_patches(feedbacks)
    assert len(patches) == 2

    # Check enrich identity patch
    p_enrich = next(p for p in patches if p["patch_type"] == "enrich_identity_answer_from_story_chunks")
    assert p_enrich["query_pattern"] == "hạ huyền sương là ai"
    assert p_enrich["target_entity"] == "Hạ Huyền Sương"
    assert p_enrich["policy"] == {"enrich_from_story_chunks": True, "target_entity": "Hạ Huyền Sương"}
    assert p_enrich["effective_status"] == "active"

    # Check prefer chapter summary patch
    p_intent = next(p for p in patches if p["patch_type"] == "prefer_chapter_summary_intent")
    assert p_intent["query_pattern"] == "nội dung chương truyện là gì"
    assert p_intent["policy"] == {"prefer_chapter_summary": True, "suppress_entities": True}


# 3. Test Pipeline Dry-run vs Write Safety
class MockSupabaseClient:
    def __init__(self):
        self.calls = []
        self.data = {
            "rag_feedback": [
                {
                    "id": "fb-1",
                    "question": "Hạ Huyền Sương là ai?",
                    "answer": "Hạ Huyền Sương là một nhân vật nữ.",
                    "user_comment": "Câu trả lời về nhân vật quá máy móc và sơ sài",
                    "status": "pending"
                }
            ],
            "oracle_answer_effective_patches": [],
            "oracle_answer_feedback_summary": [],
            "oracle_cache": []
        }

    def table(self, name):
        self.calls.append(("table", name))
        return MockTableBuilder(self, name)

class MockTableBuilder:
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def select(self, *args, **kwargs):
        self.client.calls.append(("select", self.name, args, kwargs))
        return self

    def eq(self, *args, **kwargs):
        self.client.calls.append(("eq", self.name, args, kwargs))
        return self

    def limit(self, *args, **kwargs):
        self.client.calls.append(("limit", self.name, args, kwargs))
        return self

    def upsert(self, data, *args, **kwargs):
        self.client.calls.append(("upsert", self.name, data, args, kwargs))
        return self

    def insert(self, data, *args, **kwargs):
        self.client.calls.append(("insert", self.name, data, args, kwargs))
        return self

    def update(self, data, *args, **kwargs):
        self.client.calls.append(("update", self.name, data, args, kwargs))
        return self

    def in_(self, *args, **kwargs):
        self.client.calls.append(("in_", self.name, args, kwargs))
        return self

    def execute(self):
        class Result:
            def __init__(self, data):
                self.data = data
        return Result(self.client.data.get(self.name, []))

def test_pipeline_dry_run_safety():
    mock_db = MockSupabaseClient()
    with patch("backend.scripts.run_oracle_answer_feedback_pipeline.supabase", mock_db):
        # Run dry run
        res = run_pipeline(dry_run=True, clear_cache=True)
        assert res["feedback_rows_read"] == 1
        assert res["summary_rows_written"] == 1
        assert res["patches_written"] == 1
        assert res["dry_run"] is True

        # Verify no modifying DB queries were issued
        write_actions = [c[0] for c in mock_db.calls if c[0] in ("upsert", "insert", "update", "delete")]
        assert len(write_actions) == 0

def test_pipeline_write_safety():
    mock_db = MockSupabaseClient()
    with patch("backend.scripts.run_oracle_answer_feedback_pipeline.supabase", mock_db):
        # Run write mode
        res = run_pipeline(dry_run=False, clear_cache=False)
        assert res["dry_run"] is False

        # Verify modify DB queries were issued to summaries, patches, and feedback statuses
        write_tables = [c[1] for c in mock_db.calls if c[0] in ("upsert", "insert", "update")]
        assert "oracle_answer_feedback_summary" in write_tables
        assert "oracle_answer_effective_patches" in write_tables
        assert "rag_feedback" in write_tables

        # Verify strict rules: no calls modifying wiki_entries or provisional_library
        assert "wiki_entries" not in write_tables
        assert "provisional_library" not in write_tables


# 4. Test Oracle Runtime Patch Integration (No LLM, no embedding)
@pytest.mark.asyncio
async def test_runtime_patch_integration():
    # Mock supabase responses to return active patches
    mock_db = MockSupabaseClient()
    mock_db.data["oracle_answer_effective_patches"] = [
        {
            "patch_type": "prefer_chapter_summary_intent",
            "query_pattern": "nội dung chương truyện là gì",
            "effective_status": "active",
            "policy": {"prefer_chapter_summary": True, "suppress_entities": True}
        },
        {
            "patch_type": "suppress_irrelevant_entity_expansion",
            "query_pattern": "hạ huyền sương là ai",
            "target_entity": "Hạ Huyền Sương",
            "effective_status": "active",
            "policy": {"suppress_unrelated_entities": True}
        }
    ]

    # Test local wiki context building with prefer_chapter_summary_intent active
    from backend.routes.ai_oracle import get_wiki_context, WIKI_EMPTY_CONTEXT

    # Question: nội dung chương truyện là gì
    # Active patch should suppress entities, causing it to return WIKI_EMPTY_CONTEXT (or no entities)
    mock_db.data["wiki_entries"] = [{"title": "Hạ Huyền Sương", "summary": "Nữ hoàng băng giá."}]

    # Check that prefer_chapter patch is loaded and forces WIKI_EMPTY_CONTEXT
    ctx = await get_wiki_context(
        mock_db,
        "Nội dung chương truyện là gì?",
        chapter_cap=5,
        active_patches=[mock_db.data["oracle_answer_effective_patches"][0]]
    )
    assert ctx == WIKI_EMPTY_CONTEXT or ctx == ""


@pytest.mark.asyncio
async def test_verify_feedback_runtime_logic():
    from backend.scripts.run_oracle_answer_feedback_pipeline import verify_feedback_runtime
    from unittest.mock import MagicMock, patch

    mock_supabase = MagicMock()

    fb = {
        "id": "fb-1",
        "question": "chiến dịch Lệ Giang diễn ra như thế nào?",
        "chapter_progress": 829,
        "_test_force_verification": True
    }
    with patch("backend.routes.ai_oracle.get_wiki_context", return_value="Có Chu Vấn và các zombie khác."):
        res = verify_feedback_runtime(mock_supabase, fb, [])
        assert res is False

    with patch("backend.routes.ai_oracle.get_wiki_context", return_value="Chiến dịch Lệ Giang diễn ra ác liệt."):
        res = verify_feedback_runtime(mock_supabase, fb, [])
        assert res is True

    fb_suppress = {
        "id": "fb-2",
        "question": "Hàn Phong là ai?",
        "chapter_progress": 10,
        "_test_force_verification": True
    }
    patches = [{
        "patch_type": "suppress_irrelevant_entity_expansion",
        "target_entity": "Zombie Cấp 3",
        "query_pattern": "hàn phong là ai"
    }]
    with patch("backend.routes.ai_oracle.get_wiki_context", return_value="Hàn Phong đối đầu với Zombie Cấp 3"):
        res = verify_feedback_runtime(mock_supabase, fb_suppress, patches)
        assert res is False

    with patch("backend.routes.ai_oracle.get_wiki_context", return_value="Hàn Phong là đoàn trưởng"):
        res = verify_feedback_runtime(mock_supabase, fb_suppress, patches)
        assert res is True


@pytest.mark.asyncio
async def test_pipeline_runtime_verification_split():
    from backend.scripts.run_oracle_answer_feedback_pipeline import run_oracle_answer_feedback_pipeline
    from unittest.mock import MagicMock, patch

    mock_db = MockSupabaseClient()
    mock_db.data["rag_feedback"] = [
        {
            "id": "fb-ok",
            "question": "Hàn Phong là ai?",
            "answer": "...",
            "user_comment": "comment",
            "status": "pending",
            "_test_force_verification": True
        },
        {
            "id": "fb-fail",
            "question": "chiến dịch lệ giang diễn ra như thế nào?",
            "answer": "...",
            "user_comment": "comment",
            "status": "pending",
            "_test_force_verification": True
        }
    ]

    async def mock_get_wiki_context(supabase, question, chapter_progress, active_patches):
        if "lệ giang" in question.lower():
            return "Chu Vấn xuất hiện"
        return "Hàn Phong là nhân vật chính"

    with patch("backend.scripts.run_oracle_answer_feedback_pipeline.supabase", mock_db), \
         patch("backend.routes.ai_oracle.get_wiki_context", side_effect=mock_get_wiki_context):

        res = run_oracle_answer_feedback_pipeline(mock_db, dry_run=False, limit=10, clear_cache=False)
        assert res["ok"] is True

        update_calls = [c for c in mock_db.calls if c[0] == "update"]
        updated_data = [c[2] for c in update_calls]
        assert {"status": "resolved"} in updated_data
        assert {"status": "failed_runtime_verification"} in updated_data
