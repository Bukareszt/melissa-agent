# 🎙️ Melissa - AI Voice Assistant with Memory

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![LiveKit](https://img.shields.io/badge/LiveKit-Agents-purple.svg)

**A personal voice assistant that actually remembers you.**

*Built with LiveKit Agents, Fish Audio TTS, OpenAI, and Mem0 AI Memory*

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Configuration](#-configuration) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🧠 **AI Memory (Mem0)**
Melissa doesn't just respond—she **learns**. Using Mem0 AI, she:
- Remembers your name, preferences, and personal details
- Uses semantic search to recall relevant information
- Learns automatically from every conversation
- Persists memories across sessions

### 🎤 **Natural Voice Interaction**
- **Fish Audio TTS** - Natural, expressive text-to-speech
- **OpenAI Whisper STT** - Accurate speech-to-text in English
- **Silero VAD** - Smart voice activity detection
- Real-time, low-latency conversation via LiveKit

### 🔧 **Extensible Tools**
- 📚 **Book Tracking** - Query your reading list
- 🌐 **Web Search** - DuckDuckGo search for real-time info (no API key needed!)
- 🧠 **Memory Tools** - Learn, recall, and manage memories
- Easy to add your own custom tools

### 🚀 **Easy Deployment**
- One-command startup with Docker
- Works with LiveKit Agents Playground
- Optional wake word detection (Picovoice)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (for local LiveKit server)
- API Keys:
  - [OpenAI API Key](https://platform.openai.com/api-keys) (required)
  - [Fish Audio API Key](https://fish.audio/) (required)
  - [Mem0 API Key](https://app.mem0.ai/) (optional - can use local storage)
  - [Picovoice Access Key](https://console.picovoice.ai/) (optional - for wake word)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/melissa-voice-assistant.git
cd melissa-voice-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your API keys
```

### Running Melissa

```bash
# Start everything (LiveKit server + Agent)
./start_melissa.sh
```

Then open the **[LiveKit Agents Playground](https://agents-playground.livekit.io)** and connect:
- **LiveKit URL:** `ws://localhost:7880`
- **API Key:** `devkey`
- **API Secret:** `secret`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Melissa Voice Assistant                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   LiveKit    │◄──►│   Agent      │◄──►│   Tools      │       │
│  │   Server     │    │   Session    │    │              │       │
│  │  (WebRTC)    │    │              │    │ • Books      │       │
│  └──────────────┘    └──────────────┘    │ • Web Search │       │
│         ▲                   │            │ • Memory     │       │
│         │                   ▼            └──────────────┘       │
│         │            ┌──────────────┐           │               │
│         │            │ MelissaAgent │           │               │
│         │            │              │           ▼               │
│  ┌──────────────┐    │ • STT (OpenAI)│    ┌──────────────┐      │
│  │   Client     │    │ • LLM (GPT-4) │    │   Mem0 AI    │      │
│  │ (Playground) │    │ • TTS (Fish)  │    │   Memory     │      │
│  │              │    │ • VAD (Silero)│    │              │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
melissa-voice-assistant/
├── melissa_agent.py      # Main agent with tools and LLM config
├── memory_system.py      # Mem0 AI memory integration
├── tools.py              # Book tracking & web search tools
├── wake_word.py          # Picovoice wake word detection
├── start_melissa.sh      # One-command startup script
├── requirements.txt      # Python dependencies
├── env.example           # Environment variables template
└── README.md             # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for LLM and STT |
| `FISH_AUDIO_API_KEY` | ✅ | Fish Audio API key for TTS |
| `FISH_AUDIO_VOICE_ID` | ❌ | Custom voice ID (uses default if empty) |
| `MEM0_API_KEY` | ❌ | Mem0 Cloud API key (uses local if empty) |
| `PICOVOICE_ACCESS_KEY` | ❌ | For wake word detection |
| `LIVEKIT_URL` | ✅ | LiveKit server URL |
| `LIVEKIT_API_KEY` | ✅ | LiveKit API key |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit API secret |

### Memory Options

**Mem0 Cloud (Recommended for production):**
- Set `MEM0_API_KEY` in your `.env`
- Memories stored in Mem0's managed cloud
- Better performance and scalability

**Local Mem0 (Default):**
- Leave `MEM0_API_KEY` empty
- Uses local ChromaDB for vector storage
- Memories stored in `./melissa_mem0_db/`

---

## 🛠️ Customization

### Adding Custom Tools

Create tools in `melissa_agent.py`:

```python
@function_tool()
async def my_custom_tool(self, param: str) -> str:
    """
    Description of what this tool does.
    The LLM uses this description to decide when to call it.
    """
    # Your logic here
    return "Result"
```

### Changing the Voice

1. Browse voices at [Fish Audio](https://fish.audio/discover)
2. Copy the voice ID
3. Set `FISH_AUDIO_VOICE_ID` in your `.env`

### Modifying the Personality

Edit the `instructions` in `MelissaAssistant.__init__()` in `melissa_agent.py`.

---

## 🎯 Usage Examples

Once connected, try saying:

**Memory:**
- "My name is John and I work as a software developer"
- "Remember that I prefer dark mode"
- "What do you know about me?"
- "What's my name?"

**Web Search:**
- "What's the weather in New York?"
- "Who won the last Super Bowl?"
- "Search for the latest AI news"

**Books:**
- "What books have I read?"
- "Tell me about Book 1"

**Conversation:**
- "Tell me a joke"
- "Goodbye" (ends the session)

---

## 🐳 Docker Setup

The `start_melissa.sh` script automatically handles Docker:

```bash
# Manual Docker commands if needed:

# Start LiveKit server
docker run -d \
  --name melissa-livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server \
  --dev

# Stop LiveKit server
docker stop melissa-livekit && docker rm melissa-livekit
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run the agent in dev mode
python melissa_agent.py dev
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LiveKit](https://livekit.io/) - Real-time communication platform
- [Fish Audio](https://fish.audio/) - Natural text-to-speech
- [OpenAI](https://openai.com/) - LLM and speech recognition
- [Mem0](https://mem0.ai/) - AI memory system
- [Picovoice](https://picovoice.ai/) - Wake word detection

---

<div align="center">

**Made with ❤️ for voice AI enthusiasts**

[Report Bug](https://github.com/yourusername/melissa-voice-assistant/issues) • [Request Feature](https://github.com/yourusername/melissa-voice-assistant/issues)

</div>
