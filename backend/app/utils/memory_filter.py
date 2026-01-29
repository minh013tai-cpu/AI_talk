"""
Memory filtering logic - determine what to keep and what to discard
"""

from typing import List, Dict
from datetime import datetime, timedelta
from app.models.memory import Memory


def should_keep_memory(memory: Memory, days_since_creation: int, access_count: int) -> bool:
    """
    Determine if a memory should be kept or archived
    
    Criteria:
    - High importance score (>0.7) - always keep
    - Medium importance (0.4-0.7) - keep if accessed recently or frequently
    - Low importance (<0.4) - archive if not accessed in 30+ days
    """
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
