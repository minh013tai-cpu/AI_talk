import json
import os
import time
import google.generativeai as genai
from typing import List, Dict, Optional, AsyncGenerator, Iterator
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

_LOG_PATH = r"d:\AI_talk\.cursor\debug.log"

def _dbg(loc: str, msg: str, data: dict, hid: str) -> None:
    # #region agent log
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": int(time.time() * 1000), "location": loc, "message": msg, "data": data, "sessionId": "debug-session", "hypothesisId": hid}, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # #endregion

class GeminiService:
    def __init__(self):
        keys_env = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY", "")
        self.api_keys = [key.strip() for key in keys_env.split(",") if key.strip()]
        if not self.api_keys:
            raise ValueError("GEMINI_API_KEYS must be set in environment variables")
        self.key_index = 0
        self.model_name = "gemini-2.5-flash"

    def _configure_client(self, api_key: str) -> None:
        genai.configure(api_key=api_key)

    def _rotate_key(self) -> str:
        self.key_index = (self.key_index + 1) % len(self.api_keys)
        return self.api_keys[self.key_index]

    def _generate_content_with_retry(self, prompt: str, stream: bool = False):
        attempts = len(self.api_keys)
        last_error: Optional[Exception] = None
        for attempt in range(attempts):
            api_key = self.api_keys[self.key_index]
            self._configure_client(api_key)
            # #region agent log
            _dbg("gemini_service._generate_content_with_retry:loop", "attempt_start", {"attempt": attempt, "key_index": self.key_index, "num_keys": len(self.api_keys), "key_suffix": api_key[-4:] if len(api_key) >= 4 else "?"}, "H2")
            _dbg("gemini_service._generate_content_with_retry:loop", "num_keys_check", {"attempts": attempts}, "H3")
            # #endregion
            model = genai.GenerativeModel(self.model_name)
            try:
                out = model.generate_content(prompt, stream=stream)
                # #region agent log
                _dbg("gemini_service._generate_content_with_retry:success", "generate_content_ok", {"attempt": attempt}, "H1")
                # #endregion
                return out
            except ResourceExhausted as e:
                last_error = e
                # #region agent log
                _dbg("gemini_service._generate_content_with_retry:catch", "ResourceExhausted_caught", {"attempt": attempt, "key_index_before_rotate": self.key_index, "err": str(e)[:200]}, "H1")
                # #endregion
                self._rotate_key()
                # #region agent log
                _dbg("gemini_service._generate_content_with_retry:after_rotate", "key_rotated", {"key_index_after": self.key_index}, "H2")
                # #endregion
                continue
            except Exception as e:
                last_error = e
                # #region agent log
                _dbg("gemini_service._generate_content_with_retry:catch_other", "non_ResourceExhausted", {"attempt": attempt, "etype": type(e).__name__, "err": str(e)[:200], "has_429": "429" in str(e), "has_exhausted": "exhausted" in str(e).lower() or "resource" in str(e).lower()}, "H4")
                # #endregion
                raise
        if last_error:
            # #region agent log
            _dbg("gemini_service._generate_content_with_retry:raise", "raising_last_error", {"etype": type(last_error).__name__}, "H1")
            # #endregion
            raise last_error
        # #region agent log
        _dbg("gemini_service._generate_content_with_retry:raise", "raising_all_keys_exhausted", {}, "H3")
        # #endregion
        raise ResourceExhausted("Gemini API rate limit exceeded for all keys")
    
    def generate_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        memories: Optional[List[str]] = None
    ) -> str:
        """
        Generate response from Gemini
        
        Args:
            user_message: Current user message
            system_prompt: System prompt with Tymon personality
            conversation_history: Previous messages in format [{"role": "user", "content": "..."}, ...]
            memories: List of relevant memories as strings
        """
        # Build full prompt
        full_prompt = system_prompt
        
        # Add memories if available
        if memories:
            memory_context = "\n\n=== Relevant Memories ===\n"
            for i, memory in enumerate(memories, 1):
                memory_context += f"{i}. {memory}\n"
            full_prompt += memory_context
        
        # Add conversation history
        if conversation_history:
            full_prompt += "\n\n=== Conversation History ===\n"
            for msg in conversation_history[-10:]:  # Last 10 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                full_prompt += f"{role.capitalize()}: {content}\n"
        
        # Add current message
        full_prompt += f"\n\n=== Current Message ===\nUser: {user_message}\n\nTymon:"
        
        try:
            response = self._generate_content_with_retry(full_prompt)
            return response.text
        except ResourceExhausted as e:
            raise e
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_streaming_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        memories: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from Gemini
        """
        # Build full prompt (same as generate_response)
        full_prompt = system_prompt
        
        if memories:
            memory_context = "\n\n=== Relevant Memories ===\n"
            for i, memory in enumerate(memories, 1):
                memory_context += f"{i}. {memory}\n"
            full_prompt += memory_context
        
        if conversation_history:
            full_prompt += "\n\n=== Conversation History ===\n"
            for msg in conversation_history[-10:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                full_prompt += f"{role.capitalize()}: {content}\n"
        
        full_prompt += f"\n\n=== Current Message ===\nUser: {user_message}\n\nTymon:"
        
        try:
            response = self._generate_content_with_retry(full_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except ResourceExhausted as e:
            raise e
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def extract_memories(self, conversation: str) -> List[Dict[str, str]]:
        """
        Extract potential memories from conversation using Gemini
        Returns list of dicts with 'content' and 'importance_score'
        """
        prompt = f"""Analyze the following conversation and extract important information that should be remembered long-term.

Conversation:
{conversation}

For each important piece of information, provide:
1. The memory content (what to remember)
2. Importance score (0.0 to 1.0, where 1.0 is very important)
3. Category (one of: personal_info, preference, fact, relationship, goal, other)

Format as JSON array:
[
  {{
    "content": "memory text",
    "importance_score": 0.8,
    "category": "preference"
  }}
]

Only extract truly important information. Skip greetings, small talk, or trivial details.
If nothing important, return empty array: []
"""
        try:
            response = self._generate_content_with_retry(prompt)
            import json
            # Try to parse JSON from response
            text = response.text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            memories = json.loads(text)
            return memories if isinstance(memories, list) else []
        except Exception as e:
            print(f"Error extracting memories: {e}")
            return []
    
    def generate_ai_journal(
        self,
        conversation: str,
        user_message: str,
        ai_response: str
    ) -> Dict[str, any]:
        """
        Generate AI self-reflection journal entry
        """
        prompt = f"""You are Tymon, an AI assistant. After this conversation, reflect on it.

Conversation:
User: {user_message}
Tymon: {ai_response}

Full conversation context:
{conversation}

Provide a self-reflection in JSON format:
{{
  "reflection": "Your honest reflection on the conversation - what went well, what could be improved, how you felt about it",
  "learnings": ["key learning 1", "key learning 2", ...],
  "questions_raised": ["question you asked 1", "question you asked 2", ...]
}}

Be honest and thoughtful. If you challenged the user or asked clarifying questions, mention that.
"""
        try:
            response = self._generate_content_with_retry(prompt)
            import json
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            journal = json.loads(text)
            return journal
        except Exception as e:
            print(f"Error generating AI journal: {e}")
            return {
                "reflection": "Unable to generate reflection",
                "learnings": [],
                "questions_raised": []
            }


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
