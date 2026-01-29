from typing import List, Optional
from datetime import datetime
from app.services.supabase_service import get_supabase_client
from app.services.gemini_service import get_gemini_service
from app.models.memory import Memory, MemoryCreate
from app.utils.memory_filter import filter_unimportant_memories, categorize_memory_content


class MemoryService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.gemini = get_gemini_service()
    
    def extract_and_store_memories(
        self,
        user_id: str,
        conversation_text: str
    ) -> List[Memory]:
        """
        Extract memories from conversation and store them
        """
        # Use Gemini to extract memories
        extracted = self.gemini.extract_memories(conversation_text)
        
        stored_memories = []
        for mem_data in extracted:
            content = mem_data.get("content", "")
            importance = mem_data.get("importance_score", 0.5)
            category = mem_data.get("category", "other")
            
            # If category not provided, try to infer
            if category == "other":
                category = categorize_memory_content(content)
            
            # Check if similar memory already exists
            existing = self._find_similar_memory(user_id, content)
            if existing:
                # Update existing memory (increase importance if new one is higher)
                if importance > existing.get("importance_score", 0):
                    self._update_memory(
                        existing["id"],
                        importance,
                        existing.get("access_count", 0) + 1
                    )
                stored_memories.append(Memory(**existing))
            else:
                # Create new memory
                memory = self.create_memory(
                    MemoryCreate(
                        user_id=user_id,
                        content=content,
                        importance_score=importance,
                        category=category
                    )
                )
                stored_memories.append(memory)
        
        return stored_memories
    
    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        data = {
            "user_id": memory_data.user_id,
            "content": memory_data.content,
            "importance_score": memory_data.importance_score,
            "category": memory_data.category,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0
        }
        
        result = self.supabase.table("memories").insert(data).execute()
        if result.data:
            return Memory(**result.data[0])
        raise Exception("Failed to create memory")
    
    def get_relevant_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Memory]:
        """
        Retrieve relevant memories for a conversation
        Uses simple keyword matching - could be enhanced with embeddings
        """
        # Get all memories for user
        result = self.supabase.table("memories")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("importance_score", desc=True)\
            .order("last_accessed", desc=True)\
            .limit(limit * 2)\
            .execute()
        
        if not result.data:
            return []
        
        memories = [Memory(**mem) for mem in result.data]
        
        # Filter by relevance (simple keyword matching)
        query_lower = query.lower()
        relevant = []
        for mem in memories:
            content_lower = mem.content.lower()
            # Check if query keywords appear in memory
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_lower)
            if matches > 0:
                relevant.append(mem)
                # Update access info
                self._update_memory_access(mem.id)
        
        # Sort by relevance (matches) and importance
        relevant.sort(key=lambda m: (
            sum(1 for word in query_lower.split() if word in m.content.lower()),
            m.importance_score
        ), reverse=True)
        
        # Return top N
        return relevant[:limit]
    
    def get_all_memories(self, user_id: str) -> List[Memory]:
        """Get all memories for a user"""
        result = self.supabase.table("memories")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        if not result.data:
            return []
        
        memories = [Memory(**mem) for mem in result.data]
        # Filter out unimportant ones
        return filter_unimportant_memories(memories)
    
    def _find_similar_memory(self, user_id: str, content: str) -> Optional[dict]:
        """Find if a similar memory already exists"""
        # Simple check - look for memories with similar keywords
        content_words = set(content.lower().split())
        if len(content_words) < 2:
            return None
        
        result = self.supabase.table("memories")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        if not result.data:
            return None
        
        # Find memory with most word overlap
        best_match = None
        best_score = 0
        
        for mem in result.data:
            mem_words = set(mem["content"].lower().split())
            overlap = len(content_words & mem_words)
            if overlap > best_score and overlap >= 2:
                best_score = overlap
                best_match = mem
        
        return best_match if best_score >= 2 else None
    
    def _update_memory(self, memory_id: str, importance_score: float, access_count: int):
        """Update memory importance and access count"""
        self.supabase.table("memories")\
            .update({
                "importance_score": importance_score,
                "access_count": access_count,
                "last_accessed": datetime.now().isoformat()
            })\
            .eq("id", memory_id)\
            .execute()
    
    def _update_memory_access(self, memory_id: str):
        """Update last accessed time and increment access count"""
        # Get current access count
        result = self.supabase.table("memories")\
            .select("access_count")\
            .eq("id", memory_id)\
            .execute()
        
        current_count = result.data[0].get("access_count", 0) if result.data else 0
        
        self.supabase.table("memories")\
            .update({
                "last_accessed": datetime.now().isoformat(),
                "access_count": current_count + 1
            })\
            .eq("id", memory_id)\
            .execute()
    
    def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Delete a memory"""
        result = self.supabase.table("memories")\
            .delete()\
            .eq("id", memory_id)\
            .eq("user_id", user_id)\
            .execute()
        return len(result.data) > 0


# Singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create memory service singleton"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
