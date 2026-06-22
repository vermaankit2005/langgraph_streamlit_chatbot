import os
import queue
import sqlite3
import asyncio
import threading
from typing import Annotated, TypedDict

import aiosqlite
from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

SYSTEM_PROMPT = """You are a helpful, reliable AI assistant. Give accurate, clear, and concise answers, and format responses in Markdown.
"""


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


search_tool = TavilySearch(
    max_results=3,
    topic="general",
    include_images=False,
    search_depth="advanced",
)


async def load_tools():
    client = MultiServerMCPClient(
        {
            "deepwiki": {
                "transport": "streamable_http",
                "url": "https://mcp.deepwiki.com/mcp",
            }
        }
    )

    return await client.get_tools()

mcp_tools = asyncio.run(load_tools())

tools = [search_tool] + mcp_tools


llm = ChatOpenAI(
    model="deepseek/deepseek-v4-flash",
    temperature=0.6,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)


async def chat_node(state: ChatState) -> ChatState:
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    reply = await llm_with_tools.ainvoke(messages_with_system)
    return {"messages": [reply]}


tool_node = ToolNode(tools)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

DB_PATH = "chatbot.db"

# ── PERSISTENT ASYNC LOOP ─────────────────────────────────────────────────────
# AsyncSqliteSaver (aiosqlite) connections are bound to the event loop that
# created them. Streamlit reruns on the main thread, so we run ALL async graph
# work on one long-lived background loop and create the saver on that loop.

_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True).start()


def _run_coro(coro):
    """Run a coroutine on the background loop and block for its result."""
    return asyncio.run_coroutine_threadsafe(coro, _loop).result()


async def _build_workflow():
    aconn = await aiosqlite.connect(DB_PATH)
    saver = AsyncSqliteSaver(aconn)
    await saver.setup()
    return graph.compile(checkpointer=saver)


workflow = _run_coro(_build_workflow())


# ── PUBLIC API (sync wrappers over the async graph) ───────────────────────────

def stream_assistant_reply(prompt: str, config: dict):
    """Sync generator yielding assistant text chunks.

    Produces tokens on the background loop, hands them to the main thread
    through a thread-safe queue so st.write_stream can consume them.
    """
    q: queue.Queue = queue.Queue()
    _DONE = object()

    async def _produce():
        try:
            async for chunk, _meta in workflow.astream(
                input={"messages": [HumanMessage(content=prompt)]},
                config=config,
                stream_mode="messages",
            ):
                # Only stream assistant text; skip raw tool-message output.
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    q.put(chunk.content)
        finally:
            q.put(_DONE)

    fut = asyncio.run_coroutine_threadsafe(_produce(), _loop)
    while True:
        item = q.get()
        if item is _DONE:
            break
        yield item
    fut.result()  # surface any exception raised inside _produce


def get_thread_state(thread_id: str):
    """Fetch a thread's checkpoint state (sync wrapper over aget_state)."""
    return _run_coro(
        workflow.aget_state(config={"configurable": {"thread_id": thread_id}})
    )


def get_all_unique_threads_from_state() -> list[str]:
    # Read-only listing via an independent sync connection (no checkpointer).
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.execute("SELECT DISTINCT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows] if rows else []
    except sqlite3.OperationalError:
        return []
