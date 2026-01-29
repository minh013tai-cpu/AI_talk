from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.journal import (
    UserJournal,
    UserJournalCreate,
    AIJournal,
    AIJournalCreate
)
from app.services.journal_service import get_journal_service

router = APIRouter()


@router.post("/user", response_model=UserJournal)
async def create_user_journal(journal_data: UserJournalCreate):
    """Create a new user journal entry"""
    try:
        journal_service = get_journal_service()
        return journal_service.create_user_journal(journal_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=List[UserJournal])
async def get_user_journals(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    tags: Optional[str] = None
):
    """Get user journals with optional tag filtering"""
    try:
        journal_service = get_journal_service()
        tag_list = tags.split(",") if tags else None
        return journal_service.get_user_journals(user_id, limit, offset, tag_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/search")
async def search_user_journals(user_id: str, q: str, limit: int = 20):
    """Search user journals"""
    try:
        journal_service = get_journal_service()
        return journal_service.search_user_journals(user_id, q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/entry/{journal_id}")
async def get_user_journal(journal_id: str, user_id: str):
    """Get a specific user journal entry"""
    try:
        journal_service = get_journal_service()
        journal = journal_service.get_user_journal(journal_id, user_id)
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return journal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/user/entry/{journal_id}")
async def update_user_journal(
    journal_id: str,
    user_id: str,
    content: str,
    tags: Optional[str] = None
):
    """Update a user journal entry"""
    try:
        journal_service = get_journal_service()
        tag_list = tags.split(",") if tags else None
        journal = journal_service.update_user_journal(journal_id, user_id, content, tag_list)
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return journal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/entry/{journal_id}")
async def delete_user_journal(journal_id: str, user_id: str):
    """Delete a user journal entry"""
    try:
        journal_service = get_journal_service()
        success = journal_service.delete_user_journal(journal_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Journal not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/{user_id}", response_model=List[AIJournal])
async def get_ai_journals(user_id: str, limit: int = 50, offset: int = 0):
    """Get AI journals for a user"""
    try:
        journal_service = get_journal_service()
        return journal_service.get_ai_journals(user_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/entry/{journal_id}")
async def get_ai_journal(journal_id: str, user_id: str):
    """Get a specific AI journal entry"""
    try:
        journal_service = get_journal_service()
        journal = journal_service.get_ai_journal(journal_id, user_id)
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found")
        return journal
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
