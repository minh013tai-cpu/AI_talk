"""Pytest fixtures for backend tests."""
from datetime import datetime, timedelta

import pytest

from app.models.memory import Memory


@pytest.fixture
def now():
    return datetime.now()


@pytest.fixture
def memory_high():
    """High importance memory."""
    return Memory(
        id="mem-high-1",
        user_id="user-1",
        content="User is allergic to peanuts",
        importance_score=0.85,
        category="personal_info",
        created_at=datetime.now() - timedelta(days=10),
        last_accessed=datetime.now(),
        access_count=5,
        decay_score=0.8,
        ttl_days=365,
        is_pinned=False,
        memory_type="constraint",
        source="chat",
    )


@pytest.fixture
def memory_low():
    """Low importance memory."""
    return Memory(
        id="mem-low-1",
        user_id="user-1",
        content="User said hello",
        importance_score=0.3,
        category="other",
        created_at=datetime.now() - timedelta(days=60),
        last_accessed=datetime.now() - timedelta(days=50),
        access_count=0,
        decay_score=0.1,
        ttl_days=30,
        is_pinned=False,
        memory_type="fact",
        source="chat",
    )


@pytest.fixture
def memory_pinned():
    """Pinned memory (never expired by TTL)."""
    return Memory(
        id="mem-pinned-1",
        user_id="user-1",
        content="Important pinned note",
        importance_score=0.5,
        category="goal",
        created_at=datetime.now() - timedelta(days=400),
        last_accessed=datetime.now(),
        access_count=2,
        ttl_days=180,
        is_pinned=True,
        memory_type="goal",
        source="journal",
    )
