from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserJournal(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    created_at: Optional[datetime] = None
    tags: Optional[List[str]] = None


class UserJournalCreate(BaseModel):
    user_id: str
    content: str
    tags: Optional[List[str]] = None


class AIJournal(BaseModel):
    id: Optional[str] = None
    user_id: str
    conversation_id: str
    reflection: str
    learnings: List[str]
    questions_raised: List[str]
    created_at: Optional[datetime] = None


class AIJournalCreate(BaseModel):
    user_id: str
    conversation_id: str
    reflection: str
    learnings: List[str]
    questions_raised: List[str]
