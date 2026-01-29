from fastapi import APIRouter, HTTPException
from typing import List
from app.models.memory import Memory, MemoryRetrieval
from app.services.memory_service import get_memory_service

router = APIRouter()


@router.get("/{user_id}", response_model=List[Memory])
async def get_all_memories(user_id: str):
    """Get all memories for a user"""
    try:
        memory_service = get_memory_service()
        return memory_service.get_all_memories(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/relevant", response_model=MemoryRetrieval)
async def get_relevant_memories(user_id: str, query: str, limit: int = 5):
    """Get relevant memories for a query"""
    try:
        memory_service = get_memory_service()
        memories = memory_service.get_relevant_memories(user_id, query, limit)
        return MemoryRetrieval(memories=memories, count=len(memories))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str):
    """Delete a memory"""
    try:
        memory_service = get_memory_service()
        success = memory_service.delete_memory(memory_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
