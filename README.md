# LangGraph Streamlit Chatbot

A conversational AI chatbot built with **LangGraph** + **Streamlit**, powered by **Groq** (Qwen3-32B). Responses stream token-by-token.

## Screenshot

![Chatbot UI](screenshot_chat.png)

## Stack

- **LangGraph** — stateful conversation graph with `InMemorySaver` checkpointer
- **Streamlit** — streaming chat UI with sidebar, session management, custom styling
- **Groq** — LLM inference via `langchain_groq` (model: `qwen/qwen3-32b`, `reasoning_format="hidden"`)

## Features

- Token-by-token streaming via `workflow.stream(stream_mode="messages")`
- Sidebar with **New Chat** button — starts a fresh UUID-keyed thread
- Per-session conversation history persisted in LangGraph checkpointer
- Stand-up comedian persona — every reply has a joke

## Project Structure

```
langgraph_streamlit_chatbot/
├── backend/                              # LangGraph workflows + system prompts
│   ├── chat_backend.py                   # In-memory checkpointer
│   ├── chat_database_backend.py          # SQLite checkpointer
│   └── chat_database_backend_tools.py    # SQLite checkpointer + tools (search, calculator)
└── frontend/                             # Streamlit UIs
    ├── frontend.py                       # Basic chat
    ├── streaming_threads.py              # Streaming + thread sidebar
    ├── streaming_threads_sqlite.py       # Streaming + persisted threads
    └── streaming_threads_sqlite_tools.py # Streaming + persisted threads + tools
```

## Setup

```bash
python -m pip install -r requirements.txt
python -m pip install -e .   # installs the `backend` package so frontends can import it
```

Create `.env`:

```
GROQ_API_KEY=your_key_here
```

## Run

Run from the project root:

```bash
streamlit run frontend/streaming_threads.py
```
