import streamlit as st
from langchain_core.messages import HumanMessage

from chat_backend import workflow

st.set_page_config(
    page_title="ComedyBot",
    page_icon="🎤",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 780px !important;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Title ── */
.comedybot-title {
    text-align: center;
    margin-bottom: 0.25rem;
}
.comedybot-title h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.5px;
    margin: 0;
}
.comedybot-title p {
    font-size: 0.82rem;
    color: #999;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 4px 0 0 0;
}

/* Divider */
.stage-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg,
        transparent 0%,
        #f0c040 20%,
        #f5a623 50%,
        #f0c040 80%,
        transparent 100%
    );
    margin: 0.75rem 0 1.25rem 0;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin: 6px 0 !important;
    border: 1px solid transparent !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #f7f7f8 !important;
    border-color: #e8e8ea !important;
}

/* Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #fffbf0 !important;
    border-color: #f5d76e !important;
}

/* Message text */
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] {
    color: #1a1a1a !important;
    line-height: 1.65 !important;
    font-size: 0.95rem !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border: 1.5px solid #f0c040 !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #f5a623 !important;
    box-shadow: 0 0 0 3px rgba(245, 166, 35, 0.12) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #f0c040; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="comedybot-title">
    <h1>🎤 ComedyBot</h1>
    <p>Stand-up comedian · powered by AI · zero chill</p>
</div>
<hr class="stage-divider">
""", unsafe_allow_html=True)

CONFIG = {"configurable": {"thread_id": "thread-UI"}}


def render_history():
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_input(user_input: str):
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    final_state = workflow.invoke(
        input={"messages": [HumanMessage(content=user_input)]},
        config=CONFIG,
    )
    reply = final_state["messages"][-1].content

    st.session_state["message_history"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)


if "message_history" in st.session_state:
    render_history()
else:
    st.session_state["message_history"] = []

    user_input = st.chat_input("Say something... I dare you 🎤")
if user_input:
    handle_input(user_input)
