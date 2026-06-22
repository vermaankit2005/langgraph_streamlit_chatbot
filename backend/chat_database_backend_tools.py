import os
import sqlite3
from typing import Annotated, TypedDict, Literal

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver
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


@tool
def calculate(a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]) -> float:
    """
    Tool to do simple arithmetic calculation like add, subtract, multiply and divide. It takes 3 parameters:
    :param a: float
    :param b: float
    :param operation: Literal["add", "subtract", "multiply", "divide"]
    :return: float
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b if b != 0 else 0
    return None


tools = [search_tool, calculate]

llm = ChatOpenAI(
    model="deepseek/deepseek-v4-flash",
    temperature=0.6,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
llm_with_tools = llm.bind_tools(tools)

def chat_node(state: ChatState) -> ChatState:
    messages_with_system = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    reply = llm_with_tools.invoke(messages_with_system)
    return {"messages": [reply]}

tool_node = ToolNode(tools)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

conn = sqlite3.connect("chatbot.db", check_same_thread=False)

workflow = graph.compile(checkpointer=SqliteSaver(conn))


def get_all_unique_threads_from_state() -> list[str]:
    try:
        cursor = conn.execute("SELECT DISTINCT thread_id FROM checkpoints")
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    except sqlite3.OperationalError:
        return []
