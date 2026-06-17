import streamlit as st
from langchain_core.messages import HumanMessage

from chat_backend import workflow

CONFIG = {"configurable": {"thread_id": "thread-UI"}}

def render_history():
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])


def handle_input(user_input: str):
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    final_state = workflow.invoke(
        input={"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
    )
    reply = final_state["messages"][-1].content

    st.session_state["message_history"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.text(reply)


if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
else:
    render_history()

user_input = st.chat_input("Type your message")
if user_input:
    handle_input(user_input)
