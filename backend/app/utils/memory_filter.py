"""
Memory filtering logic - determine what to keep and what to discard
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models.memory import Memory


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def get_memory_tier(importance_score: float) -> str:
    if importance_score >= 0.7:
        return "high"
    if importance_score >= 0.4:
        return "medium"
    return "low"


def compute_ttl_days(
    importance_score: float,
    memory_type: Optional[str] = None,
    stability: float = 0.5
) -> int:
    tier = get_memory_tier(importance_score)
    base_ttl = {"high": 365, "medium": 180, "low": 30}[tier]
    type_bonus = {
        "constraint": 120,
        "goal": 90,
        "relationship": 90,
        "preference": 30,
        "fact": 0
    }.get(memory_type or "fact", 0)
    stability_multiplier = 0.5 + clamp(stability, 0, 1)
    ttl_days = int((base_ttl + type_bonus) * stability_multiplier)
    return max(7, min(ttl_days, 1825))


def compute_decay_score(
    importance_score: float,
    last_accessed: Optional[datetime],
    memory_type: Optional[str] = None,
    stability: float = 0.5,
    now: Optional[datetime] = None
) -> float:
    now = now or datetime.now()
    last_accessed = last_accessed or now
    days_since = max(0, (now - last_accessed).days)
    tier = get_memory_tier(importance_score)
    base_half_life = {"high": 180, "medium": 90, "low": 30}[tier]
    type_bonus = {
        "constraint": 60,
        "goal": 45,
        "relationship": 45,
        "preference": 30,
        "fact": 0
    }.get(memory_type or "fact", 0)
    stability_multiplier = 0.6 + 0.8 * clamp(stability, 0, 1)
    effective_half_life = base_half_life * stability_multiplier + type_bonus
    decay_multiplier = max(0.1, 1 - (days_since / max(1, effective_half_life)))
    return round(importance_score * decay_multiplier, 4)


def is_memory_expired(memory: Memory, now: Optional[datetime] = None) -> bool:
    if memory.is_pinned:
        return False
    if memory.ttl_days and memory.created_at:
        now = now or datetime.now()
        days_since = (now - memory.created_at).days
        if days_since > memory.ttl_days:
            if memory.importance_score >= 0.8 and memory.access_count >= 5:
                return False
            return True
    return False


def should_keep_memory(memory: Memory, days_since_creation: int, access_count: int) -> bool:
    """
    Determine if a memory should be kept or archived
    
    Criteria:
    - High importance score (>0.7) - always keep
    - Medium importance (0.4-0.7) - keep if accessed recently or frequently
    - Low importance (<0.4) - archive if not accessed in 30+ days
    """
    if memory.is_pinned:
        return True

    if memory.ttl_days and days_since_creation > memory.ttl_days:
        if memory.importance_score >= 0.8 and access_count >= 5:
            return True
        return False

    if memory.importance_score >= 0.7:
        return True  # Always keep high importance
    
    if memory.importance_score >= 0.4:
        # Medium importance: keep if accessed in last 30 days or accessed 5+ times
        if days_since_creation < 30 or access_count >= 5:
            return True
    
    # Low importance: only keep if accessed recently
    if memory.importance_score < 0.4:
        if days_since_creation < 7 or access_count >= 3:
            return True
    
    return False


def filter_unimportant_memories(memories: List[Memory]) -> List[Memory]:
    """
    Filter out memories that are no longer relevant
    """
    now = datetime.now()
    filtered = []
    
    for memory in memories:
        if memory.created_at:
            days_since = (now - memory.created_at).days
        else:
            days_since = 0
        
        if should_keep_memory(memory, days_since, memory.access_count):
            filtered.append(memory)
    
    return filtered


def categorize_memory_content(content: str) -> str:
    """
    Simple categorization of memory content
    """
    content_lower = content.lower()
    
    if any(word in content_lower for word in ["like", "prefer", "favorite", "love", "hate", "dislike"]):
        return "preference"
    elif any(word in content_lower for word in ["name", "age", "born", "live", "from"]):
        return "personal_info"
    elif any(word in content_lower for word in ["friend", "family", "relationship", "know"]):
        return "relationship"
    elif any(word in content_lower for word in ["goal", "want", "plan", "dream", "aspire"]):
        return "goal"
    else:
        return "fact"


def infer_memory_type(content: str, category: Optional[str] = None) -> str:
    content_lower = content.lower()
    if any(word in content_lower for word in ["don't", "do not", "avoid", "cannot", "can't", "never", "allergic", "boundary", "limit"]):
        return "constraint"
    if category == "goal":
        return "goal"
    if category == "relationship":
        return "relationship"
    if category == "preference":
        return "preference"
    return "fact"
