"""
Melissa - AI Voice Assistant with Memory

A personal voice assistant that learns and remembers you.

Powered by:
- LiveKit Agents - Real-time voice AI framework
- Fish Audio - Natural text-to-speech
- OpenAI - LLM (GPT-4o-mini) and STT (Whisper)
- Mem0 AI - Intelligent memory system
- Silero - Voice activity detection

Usage:
    # With LiveKit (recommended)
    python melissa_agent.py dev
    
    # Standalone with wake word (experimental)
    python melissa_agent.py --standalone

Repository: https://github.com/yourusername/melissa-voice-assistant
License: MIT
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LiveKit Agents imports
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import Agent, AgentSession
from livekit.agents.llm import function_tool

# Plugin imports
from livekit.plugins import openai, silero
from livekit.plugins.fishaudio import TTS as FishAudioTTS

# Local modules
from tools import check_read_books, get_book_details, web_search
from memory_system import (
    mem0_learn_from_conversation,
    mem0_get_all,
    mem0_forget_all,
    mem0_get_context,
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class MelissaAssistant(Agent):
    """
    Melissa - Your personal voice assistant with Mem0 AI memory.
    
    She can:
    - Listen for the wake word "Melissa" 
    - Respond with natural voice using Fish Audio
    - Check your read books
    - Search the web for information
    - LEARN and remember things about you using Mem0 AI
    - Have natural conversations
    - End conversation on command
    """
    
    def __init__(self):
        super().__init__(
            instructions="""You are Melissa, a friendly personal voice assistant with AI-powered memory.

LANGUAGE: You ONLY speak English. Always respond in English.

MEMORY SYSTEM:
Your memory works AUTOMATICALLY in the background. You don't need to save things manually.
- When user shares info like "my name is Greg", the system learns it automatically
- Just acknowledge naturally: "Nice to meet you, Greg!" 
- Use show_what_i_know when user asks "what do you know about me?"
- Use forget_everything when user wants to reset memory

TOOLS:
- check_my_books / get_book_info - Check user's reading list
- search_the_web - Search internet for facts, news, weather
- show_what_i_know - Show all memories (when asked)
- forget_everything - Clear all memories (when asked)
- end_conversation - Use when user says goodbye/bye/stop

PERSONALITY:
- Warm, friendly, conversational
- Keep responses brief (voice interaction)
- Reference things you remember naturally

Note: Memory context will be injected automatically before each response.
""",
            stt=openai.STT(language="en"),  # OpenAI Whisper - English only
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=FishAudioTTS(
                api_key=os.environ.get("FISH_AUDIO_API_KEY"),
                reference_id=os.environ.get("FISH_AUDIO_VOICE_ID"),
                model="s1",
                latency_mode="balanced",
                sample_rate=24000,
            ),
            vad=silero.VAD.load(),  # Voice Activity Detection
        )

    # ========== BOOK TOOLS ==========
    
    @function_tool()
    async def check_my_books(self) -> str:
        """Check and list all books that I have read."""
        return await check_read_books()

    @function_tool()
    async def get_book_info(self, book_name: str) -> str:
        """Get detailed information about a specific book."""
        return await get_book_details(book_name)

    # ========== WEB SEARCH TOOL ==========
    
    @function_tool()
    async def search_the_web(self, query: str) -> str:
        """
        Search the internet using DuckDuckGo for ANY information you don't know.
        
        ALWAYS use this tool when user asks about:
        - Current events, news, recent happenings
        - Weather, sports scores, stock prices
        - Facts you're unsure about
        - "What is...", "Who is...", "When did...", "How to..."
        - Any question that requires up-to-date or factual information
        
        Args:
            query: The search query - be specific and include relevant keywords
        
        Returns:
            Search results with titles and snippets from web pages
        """
        logger.info(f"🔍 Web search requested: {query}")
        return await web_search(query)

    # ========== MEMORY TOOLS (for explicit queries only) ==========
    
    @function_tool()
    async def show_what_i_know(self) -> str:
        """
        Show all memories stored about the user.
        Use when user asks "what do you know about me?" or "what do you remember?"
        """
        return await mem0_get_all()

    @function_tool()
    async def forget_everything(self) -> str:
        """
        Delete all memories and start fresh.
        Use when user explicitly asks to forget everything or reset memory.
        """
        return await mem0_forget_all()

    # ========== SESSION CONTROL ==========
    
    @function_tool()
    async def end_conversation(self) -> str:
        """
        End the conversation session. Use when user says goodbye, bye, end conversation, etc.
        """
        logger.info("🔚 User requested to end conversation")
        await self.session.say("Goodbye! Say 'Melissa' when you need me again.")
        await self.session.aclose()
        return "Conversation ended"

    async def on_enter(self):
        """Called when the agent session starts."""
        self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    """Main agent entry point."""
    logger.info("🚀 Starting Melissa agent session...")
    
    # Connect to the room first
    await ctx.connect()
    logger.info(f"📡 Connected to room: {ctx.room.name}")
    
    # Create the session
    session = AgentSession()
    
    # Track conversation for Mem0 automatic learning
    last_user_input = ""
    
    @session.on("user_input_transcribed")
    def on_user_input(event):
        """Called when user speech is transcribed - learn from user input automatically."""
        nonlocal last_user_input
        if event.is_final:
            last_user_input = event.transcript
            logger.info(f"📝 User said: {last_user_input}")
    
    @session.on("conversation_item_added") 
    def on_conversation_item(event):
        """
        Called when a message is added to conversation.
        Mem0 AUTOMATICALLY learns from every conversation exchange.
        """
        nonlocal last_user_input
        text_preview = event.item.text_content[:100] if event.item.text_content else 'None'
        logger.info(f"💬 Conversation item: role={event.item.role}, text={text_preview}...")
        
        # When assistant responds, learn from the full exchange
        if event.item.role == "assistant" and last_user_input:
            agent_text = event.item.text_content or ""
            if agent_text:
                # Mem0 AUTOMATICALLY extracts facts from conversation
                # No tool call needed - this happens in background!
                logger.info(f"🧠 AUTO-LEARNING from: User='{last_user_input[:50]}...' Agent='{agent_text[:50]}...'")
                asyncio.create_task(
                    mem0_learn_from_conversation(last_user_input, agent_text[:500])
                )
                last_user_input = ""
    
    @session.on("function_tools_executed")
    def on_tools_executed(event):
        """Called when function tools are executed."""
        for call, output in event.zipped():
            result_preview = output.result[:200] if output.result else 'None'
            logger.info(f"🔧 TOOL EXECUTED: {call.name}({call.arguments}) -> {result_preview}")
    
    # Start the agent session with our assistant
    await session.start(
        agent=MelissaAssistant(),
        room=ctx.room,
    )
    
    logger.info("✅ Melissa is ready and listening!")


def main():
    """
    Main entry point for Melissa Voice Assistant.
    
    Usage:
        python melissa_agent.py dev      # Development mode (auto-reload)
        python melissa_agent.py start    # Production mode
    """
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )


if __name__ == "__main__":
    main()

