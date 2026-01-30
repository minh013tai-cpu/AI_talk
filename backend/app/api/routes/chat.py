from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from app.models.chat import ChatMessage, ChatResponse
from app.models.journal import AIJournalCreate
from app.services.gemini_service import get_gemini_service
from app.services.memory_service import get_memory_service
from app.services.journal_service import get_journal_service
from app.services.supabase_service import get_supabase_client
from app.utils.prompt_builder import TYMON_SYSTEM_PROMPT
from datetime import datetime
import logging
import os
import traceback
import uuid

logger = logging.getLogger(__name__)

def _is_production() -> bool:
    return os.getenv("VERCEL_ENV") == "production" or os.getenv("ENVIRONMENT") == "production"

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(message_data: ChatMessage):
    """
    Main chat endpoint - handles conversation with Tymon
    """
    try:
        supabase = get_supabase_client()
        gemini = get_gemini_service()
        memory_service = get_memory_service()
        journal_service = get_journal_service()
        
        user_id = message_data.user_id
        user_message = message_data.message
        conversation_id = message_data.conversation_id or str(uuid.uuid4())
        
        # Ensure user exists before proceeding
        from app.services.supabase_service import ensure_user_exists
        if not ensure_user_exists(user_id):
            raise HTTPException(status_code=500, detail="Failed to ensure user exists")
        
        # Get relevant memories
        memories = memory_service.get_relevant_memories(user_id, user_message, limit=5)
        memory_texts = [mem.content for mem in memories]
        
        # Get conversation history for this specific conversation (filter in Python to avoid JSONB filter syntax issues)
        history_query = supabase.table("conversations")\
            .select("message, response, timestamp, metadata")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=False)\
            .limit(100)
        history_result = history_query.execute()
        
        rows = history_result.data or []
        if conversation_id:
            rows = [r for r in rows if (r.get("metadata") or {}).get("conversation_id") == conversation_id]
        rows = rows[-10:]
        
        conversation_history = []
        for conv in rows:
            conversation_history.append({"role": "user", "content": conv["message"]})
            conversation_history.append({"role": "assistant", "content": conv["response"]})
        
        # Generate response from Gemini
        ai_response = gemini.generate_response(
            user_message=user_message,
            system_prompt=TYMON_SYSTEM_PROMPT,
            conversation_history=conversation_history,
            memories=memory_texts
        )
        
        # Store conversation
        conv_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "message": user_message,
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "conversation_id": conversation_id,
                "memories_used": len(memories)
            }
        }
        
        supabase.table("conversations").insert(conv_data).execute()
        
        # Extract and store new memories from this conversation
        conversation_text = f"User: {user_message}\nTymon: {ai_response}"
        memory_service.extract_and_store_memories(user_id, conversation_text)
        
        # Generate AI journal entry (async, don't wait)
        try:
            # Get full conversation context for journal
            full_context = "\n".join([
                f"{h['role']}: {h['content']}" 
                for h in conversation_history[-5:]
            ]) + f"\nUser: {user_message}\nTymon: {ai_response}"
            
            ai_journal_data = gemini.generate_ai_journal(
                conversation=full_context,
                user_message=user_message,
                ai_response=ai_response
            )
            
            journal_service.create_ai_journal(
                AIJournalCreate(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    reflection=ai_journal_data.get("reflection", ""),
                    learnings=ai_journal_data.get("learnings", []),
                    questions_raised=ai_journal_data.get("questions_raised", [])
                )
            )
        except Exception as e:
            print(f"Error creating AI journal: {e}")
            # Don't fail the request if journal creation fails
        
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        logger.exception("Chat POST error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)


@router.get("/history/{user_id}")
async def get_conversation_history(user_id: str, conversation_id: Optional[str] = None, limit: int = 50):
    """Get conversation history for a user, optionally filtered by conversation_id"""
    try:
        supabase = get_supabase_client()
        query = supabase.table("conversations")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=False)\
            .limit(limit * 3 if conversation_id else limit)
        result = query.execute()
        data = result.data or []
        if conversation_id:
            data = [r for r in data if (r.get("metadata") or {}).get("conversation_id") == conversation_id][:limit]
        return data
    except Exception as e:
        logger.exception("get_conversation_history error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)


@router.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get list of all conversations for a user, grouped by conversation_id, with pinned status"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("conversations")\
            .select("id, message, response, timestamp, metadata")\
            .eq("user_id", user_id)\
            .order("timestamp", desc=True)\
            .execute()
        
        if not result.data:
            return []
        
        # Fetch pinned conversations (skip if table not yet created - e.g. migration not run)
        pinned_ids = set()
        try:
            pinned_result = supabase.table("pinned_conversations")\
                .select("conversation_id")\
                .eq("user_id", user_id)\
                .execute()
            pinned_ids = {r["conversation_id"] for r in (pinned_result.data or [])}
        except Exception as pin_err:
            logger.warning("pinned_conversations table not found or error: %s - run supabase_migration_pinned.sql", pin_err)
        
        conversations_dict = {}
        for conv in result.data:
            conv_id = conv.get("metadata", {}).get("conversation_id") if conv.get("metadata") else None
            if not conv_id:
                continue
            
            if conv_id not in conversations_dict:
                conversations_dict[conv_id] = {
                    "conversation_id": conv_id,
                    "first_message": conv.get("message", "")[:50] + "..." if len(conv.get("message", "")) > 50 else conv.get("message", ""),
                    "last_message_time": conv.get("timestamp"),
                    "message_count": 0,
                    "pinned": conv_id in pinned_ids
                }
            
            conversations_dict[conv_id]["message_count"] += 1
            if conv.get("timestamp") > conversations_dict[conv_id]["last_message_time"]:
                conversations_dict[conv_id]["last_message_time"] = conv.get("timestamp")
                conversations_dict[conv_id]["first_message"] = conv.get("message", "")[:50] + "..." if len(conv.get("message", "")) > 50 else conv.get("message", "")
        
        conversations_list = list(conversations_dict.values())
        
        def _sort_key(x):
            pinned = 0 if x.get("pinned") else 1
            ts = x.get("last_message_time") or ""
            try:
                ts_val = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except (ValueError, TypeError):
                ts_val = 0
            return (pinned, -ts_val)
        
        conversations_list.sort(key=_sort_key)
        return conversations_list
    except Exception as e:
        logger.exception("get_conversations error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)


@router.delete("/conversations/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str):
    """Delete a conversation and all its messages from Supabase"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("conversations")\
            .select("id, metadata")\
            .eq("user_id", user_id)\
            .execute()
        
        rows = result.data or []
        ids_to_delete = [
            r["id"] for r in rows
            if (r.get("metadata") or {}).get("conversation_id") == conversation_id
        ]
        
        if ids_to_delete:
            for row_id in ids_to_delete:
                supabase.table("conversations").delete().eq("id", row_id).execute()
        
        # Remove from pinned_conversations if present (ignore if table not yet created)
        try:
            supabase.table("pinned_conversations")\
                .delete()\
                .eq("user_id", user_id)\
                .eq("conversation_id", conversation_id)\
                .execute()
        except Exception:
            pass
        
        return {"ok": True, "deleted": len(ids_to_delete)}
    except Exception as e:
        logger.exception("delete_conversation error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)


@router.post("/conversations/{user_id}/{conversation_id}/pin")
async def pin_conversation(user_id: str, conversation_id: str):
    """Pin a conversation"""
    try:
        supabase = get_supabase_client()
        supabase.table("pinned_conversations").upsert(
            {"user_id": user_id, "conversation_id": conversation_id, "pinned_at": datetime.now().isoformat()},
            on_conflict="user_id,conversation_id"
        ).execute()
        return {"ok": True, "pinned": True}
    except Exception as e:
        logger.exception("pin_conversation error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)


@router.delete("/conversations/{user_id}/{conversation_id}/pin")
async def unpin_conversation(user_id: str, conversation_id: str):
    """Unpin a conversation"""
    try:
        supabase = get_supabase_client()
        supabase.table("pinned_conversations")\
            .delete()\
            .eq("user_id", user_id)\
            .eq("conversation_id", conversation_id)\
            .execute()
        return {"ok": True, "pinned": False}
    except Exception as e:
        logger.exception("unpin_conversation error: %s", e)
        detail = str(e)
        if not _is_production():
            detail = f"{detail} | traceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=detail)
