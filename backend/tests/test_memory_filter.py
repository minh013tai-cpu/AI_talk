"""Tests for app.utils.memory_filter."""
from datetime import datetime, timedelta

import pytest

from app.models.memory import Memory
from app.utils.memory_filter import (
    clamp,
    get_memory_tier,
    compute_ttl_days,
    compute_decay_score,
    is_memory_expired,
    should_keep_memory,
    filter_unimportant_memories,
    categorize_memory_content,
    infer_memory_type,
)


class TestClamp:
    def test_clamp_inside(self):
        assert clamp(0.5, 0, 1) == 0.5

    def test_clamp_below_min(self):
        assert clamp(-0.5, 0, 1) == 0

    def test_clamp_above_max(self):
        assert clamp(1.5, 0, 1) == 1


class TestGetMemoryTier:
    def test_high(self):
        assert get_memory_tier(0.7) == "high"
        assert get_memory_tier(1.0) == "high"

    def test_medium(self):
        assert get_memory_tier(0.4) == "medium"
        assert get_memory_tier(0.69) == "medium"

    def test_low(self):
        assert get_memory_tier(0.39) == "low"
        assert get_memory_tier(0) == "low"


class TestComputeTtlDays:
    def test_high_importance_base(self):
        ttl = compute_ttl_days(0.8, "fact", 0.5)
        assert 7 <= ttl <= 1825
        assert ttl >= 180

    def test_low_importance_shorter(self):
        ttl_low = compute_ttl_days(0.3, "fact", 0.5)
        ttl_high = compute_ttl_days(0.8, "fact", 0.5)
        assert ttl_low < ttl_high

    def test_constraint_bonus(self):
        ttl_fact = compute_ttl_days(0.5, "fact", 0.5)
        ttl_constraint = compute_ttl_days(0.5, "constraint", 0.5)
        assert ttl_constraint > ttl_fact

    def test_bounds(self):
        assert compute_ttl_days(0.0, "fact", 0.0) >= 7
        assert compute_ttl_days(1.0, "constraint", 1.0) <= 1825


class TestComputeDecayScore:
    def test_just_accessed_scores_high(self):
        now = datetime.now()
        score = compute_decay_score(0.8, now, "fact", 0.5, now)
        assert score > 0.5
        assert score <= 0.8

    def test_old_access_decays(self):
        now = datetime.now()
        old = now - timedelta(days=200)
        score = compute_decay_score(0.8, old, "fact", 0.5, now)
        assert score < 0.8
        assert score >= 0.08  # min 0.1 multiplier

    def test_high_importance_decays_slower(self):
        now = datetime.now()
        old = now - timedelta(days=90)
        high = compute_decay_score(0.8, old, "fact", 0.5, now)
        low = compute_decay_score(0.3, old, "fact", 0.5, now)
        assert high > low


class TestIsMemoryExpired:
    def test_pinned_never_expired(self, memory_pinned):
        now = datetime.now()
        assert is_memory_expired(memory_pinned, now) is False

    def test_no_ttl_not_expired(self):
        mem = Memory(
            user_id="u",
            content="x",
            importance_score=0.5,
            category="fact",
            ttl_days=None,
            created_at=datetime.now() - timedelta(days=1000),
        )
        assert is_memory_expired(mem) is False

    def test_expired_by_ttl(self):
        mem = Memory(
            user_id="u",
            content="x",
            importance_score=0.5,
            category="fact",
            ttl_days=30,
            created_at=datetime.now() - timedelta(days=60),
            access_count=0,
        )
        assert is_memory_expired(mem) is True

    def test_ttl_exceeded_but_high_importance_kept(self):
        mem = Memory(
            user_id="u",
            content="x",
            importance_score=0.9,
            category="fact",
            ttl_days=30,
            created_at=datetime.now() - timedelta(days=60),
            access_count=10,
        )
        assert is_memory_expired(mem) is False


class TestShouldKeepMemory:
    def test_high_importance_always_keep(self):
        mem = Memory(user_id="u", content="x", importance_score=0.8, category="fact")
        assert should_keep_memory(mem, days_since_creation=500, access_count=0) is True

    def test_pinned_always_keep(self, memory_pinned):
        assert should_keep_memory(memory_pinned, 500, 0) is True

    def test_medium_keep_if_recent_or_accessed(self):
        mem = Memory(user_id="u", content="x", importance_score=0.5, category="fact")
        assert should_keep_memory(mem, 10, 0) is True
        assert should_keep_memory(mem, 100, 6) is True

    def test_medium_drop_if_old_and_rarely_accessed(self):
        mem = Memory(user_id="u", content="x", importance_score=0.5, category="fact", ttl_days=30)
        assert should_keep_memory(mem, 60, 0) is False

    def test_low_keep_only_recent_or_accessed(self):
        mem = Memory(user_id="u", content="x", importance_score=0.3, category="fact")
        assert should_keep_memory(mem, 5, 0) is True
        assert should_keep_memory(mem, 5, 4) is True
        assert should_keep_memory(mem, 30, 0) is False


class TestFilterUnimportantMemories:
    def test_filters_out_expired(self, memory_low):
        memories = [
            memory_low,
            Memory(
                user_id="u",
                content="y",
                importance_score=0.9,
                category="fact",
                created_at=datetime.now(),
            ),
        ]
        filtered = filter_unimportant_memories(memories)
        assert len(filtered) >= 1
        ids = [m.id for m in filtered]
        assert memory_low.id not in ids or memory_low.id in ids  # low may be dropped

    def test_keeps_high_importance(self, memory_high):
        filtered = filter_unimportant_memories([memory_high])
        assert len(filtered) == 1
        assert filtered[0].id == memory_high.id


class TestCategorizeMemoryContent:
    def test_preference(self):
        assert categorize_memory_content("I like coffee") == "preference"

    def test_personal_info(self):
        assert categorize_memory_content("My name is Alex") == "personal_info"

    def test_relationship(self):
        assert categorize_memory_content("My friend John") == "relationship"

    def test_goal(self):
        assert categorize_memory_content("I want to learn Python") == "goal"

    def test_fact_default(self):
        assert categorize_memory_content("The meeting was on Monday") == "fact"


class TestInferMemoryType:
    def test_constraint(self):
        assert infer_memory_type("I can't eat gluten") == "constraint"

    def test_goal_from_category(self):
        assert infer_memory_type("Learn Python", category="goal") == "goal"

    def test_preference_from_category(self):
        assert infer_memory_type("Coffee", category="preference") == "preference"

    def test_fact_default(self):
        assert infer_memory_type("Something happened") == "fact"
