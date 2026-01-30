from typing import List, Optional
from datetime import datetime
from app.services.supabase_service import get_supabase_client
from app.models.journal import UserJournal, UserJournalCreate, AIJournal, AIJournalCreate
from app.services.memory_service import get_memory_service


class JournalService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    # User Journal methods
    def create_user_journal(self, journal_data: UserJournalCreate) -> UserJournal:
        """Create a new user journal entry"""
        data = {
            "user_id": journal_data.user_id,
            "content": journal_data.content,
            "tags": journal_data.tags or [],
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("user_journals").insert(data).execute()
        if result.data:
            journal = UserJournal(**result.data[0])
            try:
                memory_service = get_memory_service()
                journal_text = f"User journal entry:\n{journal_data.content}"
                memory_service.extract_and_store_memories(
                    journal_data.user_id,
                    journal_text,
                    source="journal"
                )
            except Exception as e:
                print(f"Error extracting memories from journal: {e}")
            return journal
        raise Exception("Failed to create user journal")
    
    def get_user_journals(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        tags: Optional[List[str]] = None
    ) -> List[UserJournal]:
        """Get user journals with optional tag filtering"""
        query = self.supabase.table("user_journals")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)
        
        if tags:
            # Filter by tags (Supabase array contains)
            for tag in tags:
                query = query.contains("tags", [tag])
        
        result = query.execute()
        
        if not result.data:
            return []
        
        return [UserJournal(**journal) for journal in result.data]
    
    def get_user_journal(self, journal_id: str, user_id: str) -> Optional[UserJournal]:
        """Get a specific user journal entry"""
        result = self.supabase.table("user_journals")\
            .select("*")\
            .eq("id", journal_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data:
            return UserJournal(**result.data[0])
        return None
    
    def update_user_journal(
        self,
        journal_id: str,
        user_id: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> Optional[UserJournal]:
        """Update a user journal entry"""
        update_data = {"content": content}
        if tags is not None:
            update_data["tags"] = tags
        
        result = self.supabase.table("user_journals")\
            .update(update_data)\
            .eq("id", journal_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data:
            return UserJournal(**result.data[0])
        return None
    
    def delete_user_journal(self, journal_id: str, user_id: str) -> bool:
        """Delete a user journal entry"""
        result = self.supabase.table("user_journals")\
            .delete()\
            .eq("id", journal_id)\
            .eq("user_id", user_id)\
            .execute()
        return len(result.data) > 0
    
    def search_user_journals(
        self,
        user_id: str,
        search_query: str,
        limit: int = 20
    ) -> List[UserJournal]:
        """Search user journals by content"""
        # Simple text search - could be enhanced with full-text search
        result = self.supabase.table("user_journals")\
            .select("*")\
            .eq("user_id", user_id)\
            .ilike("content", f"%{search_query}%")\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        if not result.data:
            return []
        
        return [UserJournal(**journal) for journal in result.data]
    
    # AI Journal methods
    def create_ai_journal(self, journal_data: AIJournalCreate) -> AIJournal:
        """Create a new AI journal entry"""
        data = {
            "user_id": journal_data.user_id,
            "conversation_id": journal_data.conversation_id,
            "reflection": journal_data.reflection,
            "learnings": journal_data.learnings,
            "questions_raised": journal_data.questions_raised,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("ai_journals").insert(data).execute()
        if result.data:
            return AIJournal(**result.data[0])
        raise Exception("Failed to create AI journal")
    
    def get_ai_journals(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AIJournal]:
        """Get AI journals for a user"""
        result = self.supabase.table("ai_journals")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        if not result.data:
            return []
        
        return [AIJournal(**journal) for journal in result.data]
    
    def get_ai_journal(self, journal_id: str, user_id: str) -> Optional[AIJournal]:
        """Get a specific AI journal entry"""
        result = self.supabase.table("ai_journals")\
            .select("*")\
            .eq("id", journal_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if result.data:
            return AIJournal(**result.data[0])
        return None


# Singleton instance
_journal_service: Optional[JournalService] = None


def get_journal_service() -> JournalService:
    """Get or create journal service singleton"""
    global _journal_service
    if _journal_service is None:
        _journal_service = JournalService()
    return _journal_service
