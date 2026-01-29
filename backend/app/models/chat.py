from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: datetime


class Conversation(BaseModel):
    id: str
    user_id: str
    message: str
    response: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
