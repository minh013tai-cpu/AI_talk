from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.supabase_service import get_supabase_client
from app.services.gemini_service import get_gemini_service
from app.models.memory import Memory, MemoryCreate
from app.utils.memory_filter import (
    filter_unimportant_memories,
    categorize_memory_content,
    infer_memory_type,
    compute_ttl_days,
    compute_decay_score,
    is_memory_expired,
    clamp
)


class MemoryService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.gemini = get_gemini_service()
        self.max_memories_per_user = 500
        self.max_relevance_pool = 25
    
    def extract_and_store_memories(
        self,
        user_id: str,
        conversation_text: str,
        source: str = "chat"
    ) -> List[Memory]:
        """
        Extract memories from conversation and store them
        """
        # Use Gemini to extract memories
        extracted = self.gemini.extract_memories(conversation_text)
        
        stored_memories = []
        for mem_data in extracted:
            content = mem_data.get("content", "").strip()
            if not content:
                continue
            importance = float(mem_data.get("importance_score", 0.5))
            importance = clamp(importance, 0, 1)
            category = mem_data.get("category", "other")
            memory_type = mem_data.get("memory_type") or ""
            stability = float(mem_data.get("stability", 0.5))
            stability = clamp(stability, 0, 1)
            
            # If category not provided, try to infer
            if category == "other":
                category = categorize_memory_content(content)

            if not memory_type:
                memory_type = infer_memory_type(content, category)

            adjusted_importance = self._apply_importance_rules(
                importance,
                memory_type,
                category,
                stability,
                content,
                source
            )

            ttl_days = int(mem_data.get("ttl_days", 0) or 0)
            if ttl_days <= 0:
                ttl_days = compute_ttl_days(adjusted_importance, memory_type, stability)
            else:
                ttl_days = max(7, min(ttl_days, 1825))

            now = datetime.now()
            decay_score = compute_decay_score(adjusted_importance, now, memory_type, stability, now)
            
            # Check if similar memory already exists
            existing = self._find_similar_memory(user_id, content)
            if existing:
                updated = self._merge_with_existing(
                    existing=existing,
                    adjusted_importance=adjusted_importance,
                    category=category,
                    memory_type=memory_type,
                    ttl_days=ttl_days,
                    decay_score=decay_score,
                    source=source
                )
                stored_memories.append(Memory(**updated))
            else:
                # Create new memory
                memory = self.create_memory(
                    MemoryCreate(
                        user_id=user_id,
                        content=content,
                        importance_score=adjusted_importance,
                        category=category,
                        decay_score=decay_score,
                        ttl_days=ttl_days,
                        last_used_in_chat=now,
                        is_pinned=False,
                        memory_type=memory_type,
                        source=source
                    )
                )
                stored_memories.append(memory)
        
        self.prune_memories(user_id)
        return stored_memories
    
    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        now = datetime.now().isoformat()
        decay_score = memory_data.decay_score
        if decay_score is None:
            decay_score = compute_decay_score(
                memory_data.importance_score,
                datetime.now(),
                memory_data.memory_type or "fact",
                0.5,
                datetime.now()
            )
        data = {
            "user_id": memory_data.user_id,
            "content": memory_data.content,
            "importance_score": memory_data.importance_score,
            "category": memory_data.category,
            "created_at": now,
            "last_accessed": now,
            "access_count": 0,
            "decay_score": decay_score,
            "ttl_days": memory_data.ttl_days,
            "last_used_in_chat": memory_data.last_used_in_chat or now,
            "is_pinned": memory_data.is_pinned if memory_data.is_pinned is not None else False,
            "memory_type": memory_data.memory_type or "fact",
            "source": memory_data.source or "chat"
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
            .limit(self.max_relevance_pool)\
            .execute()
        
        if not result.data:
            return []
        
        now = datetime.now()
        memories = [Memory(**mem) for mem in result.data]
        
        # Filter by relevance (simple keyword matching)
        query_lower = query.lower()
        relevant = []
        for mem in memories:
            if is_memory_expired(mem, now):
                continue
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
            m.decay_score or m.importance_score
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
    
    def _update_memory(self, memory_id: str, updates: Dict[str, Any]):
        """Update memory fields"""
        self.supabase.table("memories")\
            .update(updates)\
            .eq("id", memory_id)\
            .execute()
    
    def _update_memory_access(self, memory_id: str):
        """Update last accessed time and increment access count"""
        # Get current access count
        result = self.supabase.table("memories")\
            .select("access_count, importance_score, memory_type, last_accessed, decay_score")\
            .eq("id", memory_id)\
            .execute()
        
        current_count = result.data[0].get("access_count", 0) if result.data else 0
        importance_score = result.data[0].get("importance_score", 0.5) if result.data else 0.5
        memory_type = result.data[0].get("memory_type", "fact") if result.data else "fact"
        last_accessed = result.data[0].get("last_accessed") if result.data else None
        new_decay = compute_decay_score(
            importance_score,
            last_accessed,
            memory_type,
            0.5,
            datetime.now()
        )

        self.supabase.table("memories")\
            .update({
                "last_accessed": datetime.now().isoformat(),
                "last_used_in_chat": datetime.now().isoformat(),
                "decay_score": new_decay,
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

    def prune_memories(self, user_id: str):
        """Remove expired and low-value memories to fit budget."""
        result = self.supabase.table("memories")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        if not result.data:
            return

        now = datetime.now()
        memories = [Memory(**mem) for mem in result.data]

        expired_ids = [
            mem.id for mem in memories
            if mem.id and is_memory_expired(mem, now)
        ]

        for mem_id in expired_ids:
            self.supabase.table("memories")\
                .delete()\
                .eq("id", mem_id)\
                .eq("user_id", user_id)\
                .execute()

        remaining = [mem for mem in memories if mem.id not in set(expired_ids)]
        if len(remaining) <= self.max_memories_per_user:
            return

        candidates = [mem for mem in remaining if not mem.is_pinned]
        candidates.sort(key=lambda mem: (
            mem.decay_score or mem.importance_score,
            mem.importance_score,
            mem.created_at or now
        ))

        to_remove = len(remaining) - self.max_memories_per_user
        for mem in candidates[:to_remove]:
            if mem.id:
                self.supabase.table("memories")\
                    .delete()\
                    .eq("id", mem.id)\
                    .eq("user_id", user_id)\
                    .execute()

    def _apply_importance_rules(
        self,
        importance: float,
        memory_type: str,
        category: str,
        stability: float,
        content: str,
        source: str
    ) -> float:
        importance = clamp(importance, 0, 1)
        type_bonus = {
            "constraint": 0.15,
            "goal": 0.1,
            "relationship": 0.1,
            "preference": 0.05,
            "fact": 0.0
        }.get(memory_type, 0.0)
        category_bonus = 0.05 if category == "personal_info" else 0.0
        source_bonus = 0.15 if source == "journal" else 0.0
        stability_multiplier = 0.6 + 0.8 * clamp(stability, 0, 1)
        length_penalty = 0.1 if len(content.split()) < 4 else 0.0
        adjusted = importance * stability_multiplier + type_bonus + category_bonus + source_bonus - length_penalty
        return clamp(adjusted, 0, 1)

    def _merge_with_existing(
        self,
        existing: Dict[str, Any],
        adjusted_importance: float,
        category: str,
        memory_type: str,
        ttl_days: int,
        decay_score: float,
        source: str
    ) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        existing_importance = existing.get("importance_score", 0)
        existing_type = existing.get("memory_type")
        merged_type = existing_type or memory_type
        if memory_type in ["constraint", "goal"] and existing_type not in ["constraint", "goal"]:
            merged_type = memory_type
        existing_source = existing.get("source") or "chat"
        merged_source = "journal" if source == "journal" or existing_source == "journal" else existing_source

        updated = {
            "importance_score": max(existing_importance, adjusted_importance),
            "access_count": existing.get("access_count", 0) + 1,
            "last_accessed": now,
            "last_used_in_chat": now,
            "decay_score": max(existing.get("decay_score", 0) or 0, decay_score),
            "ttl_days": max(existing.get("ttl_days", 0) or 0, ttl_days),
            "category": existing.get("category") or category,
            "memory_type": merged_type,
            "source": merged_source
        }
        self._update_memory(existing["id"], updated)
        merged = {**existing, **updated}
        return merged


# Singleton instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create memory service singleton"""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service
