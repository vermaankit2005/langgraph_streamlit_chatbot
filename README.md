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
├── chat_backend.py                   # LangGraph workflow + system prompt
└── streamlit_streaming_frontend.py   # Streamlit UI (streaming)
```

## Setup

```bash
pip install streamlit langgraph langchain-groq langchain-core python-dotenv
```

Create `.env`:

```
GROQ_API_KEY=your_key_here
```

## Run

```bash
streamlit run streamlit_streaming_with_threads.py
```
