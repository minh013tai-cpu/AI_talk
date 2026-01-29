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


class MemoryCreate(BaseModel):
    user_id: str
    content: str
    importance_score: float
    category: str


class MemoryRetrieval(BaseModel):
    memories: List[Memory]
    count: int
