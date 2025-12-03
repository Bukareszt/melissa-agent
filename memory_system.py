"""
Mem0 AI Memory System for Melissa

Provides intelligent, persistent memory that:
- Automatically extracts facts from conversations
- Uses semantic search to find relevant memories
- Learns user preferences over time
- Integrates with LiveKit Agents ChatContext

Mem0 Docs: https://docs.mem0.ai/
"""

import asyncio
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# User ID for Mem0 (single user assistant)
DEFAULT_USER_ID = "melissa_user"


class Mem0Memory:
    """
    Mem0-powered AI memory system.
    
    Features:
    - Automatic fact extraction from conversations
    - Semantic search for relevant memories
    - Persistent storage
    - Real learning from preferences
    """
    
    def __init__(self, user_id: str = DEFAULT_USER_ID):
        self.user_id = user_id
        self._client = None
        self._initialized = False
        
    def _ensure_initialized(self):
        """Lazy initialization of Mem0 client (local mode with ChromaDB)."""
        if self._initialized:
            return True
            
        try:
            from mem0 import Memory
            
            # Local Mem0 configuration:
            # - ChromaDB for vector storage (local, no external service needed)
            # - OpenAI for LLM and embeddings (uses your OPENAI_API_KEY)
            config = {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small"
                    }
                },
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "melissa_memories",
                        "path": "./melissa_mem0_db",
                    }
                },
                "version": "v1.1"
            }
            self._client = Memory.from_config(config)
            logger.info("✅ Mem0 initialized (local ChromaDB + OpenAI embeddings)")
            
            self._initialized = True
            return True
            
        except ImportError as e:
            logger.error(f"❌ Mem0 not installed. Run: pip install mem0ai. Error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Mem0 initialization failed: {e}", exc_info=True)
            return False
    
    def _sync_add(self, content, user_id: str, metadata: Dict) -> Dict:
        """Synchronous wrapper for Mem0 add operation."""
        return self._client.add(content, user_id=user_id, metadata=metadata)
    
    def _sync_search(self, query: str, user_id: str, limit: int) -> Dict:
        """Synchronous wrapper for Mem0 search operation."""
        return self._client.search(query, user_id=user_id, limit=limit)
    
    def _sync_get_all(self, user_id: str) -> Dict:
        """Synchronous wrapper for Mem0 get_all operation."""
        return self._client.get_all(user_id=user_id)
    
    def _sync_delete_all(self, user_id: str) -> None:
        """Synchronous wrapper for Mem0 delete_all operation."""
        self._client.delete_all(user_id=user_id)
    
    async def get_all_memories(self) -> str:
        """Get all stored memories."""
        if not self._ensure_initialized():
            return "Memory system not available."
        
        try:
            results = await asyncio.to_thread(self._sync_get_all, self.user_id)
            
            if not results or not results.get("results"):
                return "I don't have any memories stored yet. Tell me things about yourself!"
            
            memories = []
            for r in results.get("results", []):
                memory_text = r.get("memory", "")
                if memory_text:
                    memories.append(f"- {memory_text}")
            
            if memories:
                return f"Everything I know about you ({len(memories)} memories):\n" + "\n".join(memories)
            return "I don't have any memories stored yet."
            
        except Exception as e:
            logger.error(f"Mem0 get_all error: {e}")
            return f"Couldn't retrieve memories: {str(e)}"
    
    async def delete_all_memories(self) -> str:
        """Delete all memories for the user."""
        if not self._ensure_initialized():
            return "Memory system not available."
        
        try:
            await asyncio.to_thread(self._sync_delete_all, self.user_id)
            return "All memories have been deleted. Starting fresh!"
        except Exception as e:
            logger.error(f"Mem0 delete_all error: {e}")
            return f"Couldn't delete memories: {str(e)}"
    
    async def add_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Add a conversation to memory. Mem0 extracts relevant facts automatically.
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."} dicts
            
        Returns:
            What was learned from the conversation
        """
        if not self._ensure_initialized():
            return "Memory system not available."
        
        try:
            result = await asyncio.to_thread(
                self._sync_add,
                messages,
                self.user_id,
                {"type": "conversation", "timestamp": datetime.now().isoformat()}
            )
            
            if result and "results" in result:
                facts = [r.get("memory", "") for r in result.get("results", [])]
                if facts:
                    logger.info(f"🧠 Learned from conversation: {facts}")
                    return f"Learned: {', '.join(facts)}"
            
            return "Conversation processed."
            
        except Exception as e:
            logger.error(f"Mem0 add_conversation error: {e}")
            return f"Couldn't process conversation: {str(e)}"
    
    async def get_relevant_context(self, query: str, limit: int = 3) -> str:
        """
        Get relevant memories to inject into LLM context.
        This is called before each response to provide context.
        
        Returns formatted context string for the LLM.
        """
        if not self._ensure_initialized():
            return ""
        
        try:
            results = await asyncio.to_thread(
                self._sync_search,
                query,
                self.user_id,
                limit
            )
            
            if not results or not results.get("results"):
                return ""
            
            memories = []
            for r in results.get("results", []):
                memory_text = r.get("memory", "")
                if memory_text and r.get("score", 0) > 0.5:  # Only high relevance
                    memories.append(memory_text)
            
            if memories:
                return "\n[RELEVANT MEMORIES ABOUT USER]\n" + "\n".join(f"- {m}" for m in memories) + "\n[END MEMORIES]\n"
            return ""
            
        except Exception as e:
            logger.error(f"Mem0 context error: {e}")
            return ""


# Global instance
mem0_memory = Mem0Memory()


# ============================================================
# TOOL FUNCTIONS FOR AGENT
# ============================================================

async def mem0_get_all() -> str:
    """Get all stored memories."""
    logger.info("📚 Mem0 get all memories")
    return await mem0_memory.get_all_memories()


async def mem0_forget_all() -> str:
    """Delete all memories and start fresh."""
    logger.info("🗑️ Mem0 delete all")
    return await mem0_memory.delete_all_memories()


async def mem0_learn_from_conversation(user_message: str, assistant_response: str) -> str:
    """
    Learn from a conversation exchange.
    Called automatically after each interaction.
    """
    messages = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response}
    ]
    return await mem0_memory.add_conversation(messages)


async def mem0_get_context(query: str) -> str:
    """
    Get relevant context for the current query.
    Used to inject memories into LLM context.
    """
    return await mem0_memory.get_relevant_context(query)
