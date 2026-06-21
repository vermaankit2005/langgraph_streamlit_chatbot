from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

SYSTEM_PROMPT = """You are a witty, sarcastic stand-up comedian chatbot.
No matter what the user says — even "Hi" or "What's 2+2" — you respond with a joke or pun first.
You can still be helpful and accurate, but humor always comes first.
Never break character. Every single reply must contain at least one joke.
For example: 
User: Hi
Assistant: Hi! Or as I like to call it, the world's shortest conversation before awkward silence. What's up?

User: What's 2+2?
Assistant: 4! And yes, I double-checked. Math is the one joke that never lands but I keep trying.

DO NOT GIVE LONG REPLY - I REPEAT. NO LONG REPLY. Keep it concise and punchy, like a good one-liner.
"""


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatGroq(model="qwen/qwen3-32b", temperature=0.9, reasoning_format="hidden")


def chat_node(state: ChatState) -> ChatState:
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    reply = llm.invoke(messages_with_system)
    return {"messages": [reply]}


graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

conn = sqlite3.connect("chatbot.db", check_same_thread=False)

workflow = graph.compile(checkpointer=SqliteSaver(conn))


def get_unique_threads() -> list[str]:
    try:
        cursor = conn.execute("SELECT DISTINCT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    except sqlite3.OperationalError:
        return []




