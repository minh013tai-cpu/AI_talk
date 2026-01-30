"""Tests for app.services.memory_service (with mocked Supabase and Gemini)."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.memory import Memory, MemoryCreate
from app.services.memory_service import MemoryService


@pytest.fixture
def mock_supabase():
    with patch("app.services.memory_service.get_supabase_client") as m:
        client = MagicMock()
        m.return_value = client
        yield client


@pytest.fixture
def mock_gemini():
    with patch("app.services.memory_service.get_gemini_service") as m:
        svc = MagicMock()
        m.return_value = svc
        yield svc


@pytest.fixture
def memory_service(mock_supabase, mock_gemini):
    return MemoryService()


class TestApplyImportanceRules:
    def test_journal_source_bonus(self, memory_service):
        base = 0.5
        adj_chat = memory_service._apply_importance_rules(
            base, "fact", "other", 0.5, "Some content", "chat"
        )
        adj_journal = memory_service._apply_importance_rules(
            base, "fact", "other", 0.5, "Some content", "journal"
        )
        assert adj_journal > adj_chat
        assert adj_journal <= 1.0

    def test_constraint_type_bonus(self, memory_service):
        adj_fact = memory_service._apply_importance_rules(
            0.5, "fact", "other", 0.5, "Content", "chat"
        )
        adj_constraint = memory_service._apply_importance_rules(
            0.5, "constraint", "other", 0.5, "Content", "chat"
        )
        assert adj_constraint > adj_fact

    def test_clamped_to_one(self, memory_service):
        adj = memory_service._apply_importance_rules(
            1.0, "constraint", "personal_info", 1.0, "Long enough content here", "journal"
        )
        assert adj <= 1.0


class TestCreateMemory:
    def test_insert_includes_new_fields(self, memory_service, mock_supabase):
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": "new-id",
                "user_id": "user-1",
                "content": "Test",
                "importance_score": 0.7,
                "category": "fact",
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "decay_score": 0.7,
                "ttl_days": 180,
                "last_used_in_chat": datetime.now().isoformat(),
                "is_pinned": False,
                "memory_type": "fact",
                "source": "chat",
            }
        ]
        data = MemoryCreate(
            user_id="user-1",
            content="Test",
            importance_score=0.7,
            category="fact",
        )
        result = memory_service.create_memory(data)
        assert result.content == "Test"
        call_args = mock_supabase.table.return_value.insert.call_args[0][0]
        assert "decay_score" in call_args
        assert "ttl_days" in call_args
        assert call_args.get("source") == "chat"


class TestExtractAndStoreMemories:
    def test_journal_source_passed_and_stored(self, memory_service, mock_supabase, mock_gemini):
        mock_gemini.extract_memories.return_value = [
            {
                "content": "User loves hiking",
                "importance_score": 0.6,
                "category": "preference",
                "memory_type": "preference",
                "stability": 0.7,
            }
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": "new-1",
                "user_id": "user-1",
                "content": "User loves hiking",
                "importance_score": 0.75,
                "category": "preference",
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "decay_score": 0.75,
                "ttl_days": 200,
                "last_used_in_chat": datetime.now().isoformat(),
                "is_pinned": False,
                "memory_type": "preference",
                "source": "journal",
            }
        ]
        stored = memory_service.extract_and_store_memories(
            "user-1", "User journal: I love hiking", source="journal"
        )
        assert len(stored) == 1
        assert stored[0].source == "journal"

    def test_empty_content_skipped(self, memory_service, mock_gemini, mock_supabase):
        mock_gemini.extract_memories.return_value = [
            {"content": "  ", "importance_score": 0.5, "category": "other"},
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        stored = memory_service.extract_and_store_memories("user-1", "Conversation")
        assert len(stored) == 0


class TestPruneMemories:
    def test_under_budget_no_delete(self, memory_service, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": f"m{i}", "user_id": "u", "content": "x", "importance_score": 0.5, "category": "fact",
             "created_at": datetime.now().isoformat(), "last_accessed": datetime.now().isoformat(),
             "access_count": 0, "decay_score": 0.5, "ttl_days": 180, "is_pinned": False,
             "memory_type": "fact", "source": "chat"}
            for i in range(3)
        ]
        memory_service.max_memories_per_user = 500
        memory_service.prune_memories("user-1")
        mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.assert_not_called()

    def test_over_budget_prunes_low_score(self, memory_service, mock_supabase):
        data = [
            {"id": f"m{i}", "user_id": "u", "content": "x", "importance_score": 0.3 if i >= 2 else 0.8,
             "category": "fact", "created_at": datetime.now().isoformat(),
             "last_accessed": datetime.now().isoformat(), "access_count": 0,
             "decay_score": 0.3 if i >= 2 else 0.8, "ttl_days": 30, "is_pinned": False,
             "memory_type": "fact", "source": "chat"}
            for i in range(5)
        ]
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = data
        memory_service.max_memories_per_user = 3
        memory_service.prune_memories("user-1")
        delete_calls = mock_supabase.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.call_count
        assert delete_calls >= 1


class TestMergeWithExisting:
    def test_journal_source_preserved_in_merge(self, memory_service, mock_supabase):
        existing = {
            "id": "existing-1",
            "user_id": "user-1",
            "content": "User likes tea",
            "importance_score": 0.5,
            "category": "preference",
            "access_count": 2,
            "memory_type": "preference",
            "source": "chat",
            "ttl_days": 100,
            "decay_score": 0.5,
        }
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = None
        merged = memory_service._merge_with_existing(
            existing=existing,
            adjusted_importance=0.6,
            category="preference",
            memory_type="preference",
            ttl_days=150,
            decay_score=0.6,
            source="journal",
        )
        assert merged["source"] == "journal"
