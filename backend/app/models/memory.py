from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Memory(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    importance_score: float
    category: str
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    decay_score: Optional[float] = None
    ttl_days: Optional[int] = None
    last_used_in_chat: Optional[datetime] = None
    is_pinned: Optional[bool] = None
    memory_type: Optional[str] = None
    source: Optional[str] = None


class MemoryCreate(BaseModel):
    user_id: str
    content: str
    importance_score: float
    category: str
    decay_score: Optional[float] = None
    ttl_days: Optional[int] = None
    last_used_in_chat: Optional[datetime] = None
    is_pinned: Optional[bool] = None
    memory_type: Optional[str] = None
    source: Optional[str] = None


class MemoryRetrieval(BaseModel):
    memories: List[Memory]
    count: int
