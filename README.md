# 🤖 Ravida — AI Business Search Agent

> An intelligent business advisor powered by LangChain, LangGraph, and Streamlit. Ravida searches the web in real time, reasons like a senior founder, and delivers sharp, actionable business insights — not generic advice.

---

## ✨ Features

- 🔍 **Real-time web search** — powered by Google Serper API, searches before every answer
- 🧠 **Persistent memory** — remembers the full conversation context across turns
- ⚡ **Live streaming** — responses stream token by token, just like ChatGPT
- 📊 **Execution transparency** — expandable status bar shows every search step as it happens
- 🔗 **Clickable sources** — all sources rendered as clean, clickable link buttons
- 🤖 **Multi-model support** — switch between Groq (Llama 3.3 70B), Gemini 2.5 Flash, and local Gemma 3 via Ollama
- 🔄 **Automatic rate limit handling** — detects rate limit errors, auto-switches to next available model
- ⏱️ **Timestamps** — every message shows time sent
- 🛡️ **Error recovery** — graceful error handling, users never see raw API errors

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM Orchestration** | LangChain + LangGraph |
| **Agent Framework** | `create_agent` with ReAct pattern |
| **Memory** | LangGraph `MemorySaver` |
| **Search Tool** | Google Serper API |
| **Frontend** | Streamlit |
| **LLM Providers** | Groq, Google Gemini, Ollama (local) |
| **Environment** | Python 3.13, `.venv` |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/ravida-agent.git
cd ravida-agent
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
SERPER_API_KEY=your_serper_api_key
```

Get your API keys:
- Groq: https://console.groq.com
- Google Gemini: https://aistudio.google.com
- Serper: https://serper.dev

### 5. (Optional) Set up local model with Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Gemma 3
ollama pull gemma3:1b
```

### 6. Run the app
```bash
streamlit run main.py
```

---

## 📁 Project Structure

```
ravida-agent/
├── main.py           # Main Streamlit app
├── prompt.py         # System prompt for the agent
├── llm_changer.py    # Multi-model LLM factory
├── .env              # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

```
User sends message
        ↓
Agent decides: search or answer directly?
        ↓
If search → Google Serper API called
        ↓
Results processed and summarized
        ↓
Final answer streamed token by token
        ↓
Sources extracted and shown as buttons
```

The agent uses LangGraph's message streaming with `stream_mode="messages"` to stream tokens in real time while also capturing tool call events to show live execution steps.

---

## 🤝 Models Supported

| Model | Provider | Best For |
|---|---|---|
| Llama 3.3 70B | Groq | Fast, reliable tool calling |
| Gemini 2.5 Flash | Google | Complex reasoning |
| Gemma 3 1B | Ollama (Local) | Offline, zero cost |

---

## 📌 Roadmap

- [ ] RAG system — chat with uploaded documents
- [ ] Multi-agent orchestration — researcher + analyst + writer agents
- [ ] FastAPI backend
- [ ] PostgreSQL persistent memory
- [ ] NextJS frontend
- [ ] Docker deployment
- [ ] User authentication

---

## 👤 Author

**Tridib** — 16 year old builder, AI agency founder in the making.

Building towards launching **Ravida AI Agency** — December 2025.

> *"learning and building is the key of creativity."*

---

## 📄 License

MIT License — free to use, modify, and distribute.