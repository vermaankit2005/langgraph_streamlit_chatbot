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

/* Stage backdrop: spotlight from top + red curtain hints on sides */
.stApp {
    background:
        radial-gradient(ellipse 55% 35% at 50% -2%,
            rgba(255, 210, 60, 0.22) 0%,
            rgba(255, 160, 20, 0.08) 45%,
            transparent 65%
        ),
        radial-gradient(ellipse 18% 80% at 0% 50%,
            rgba(160, 10, 10, 0.12) 0%,
            transparent 70%
        ),
        radial-gradient(ellipse 18% 80% at 100% 50%,
            rgba(160, 10, 10, 0.12) 0%,
            transparent 70%
        ),
        linear-gradient(180deg, #060606 0%, #020202 100%);
    min-height: 100vh;
}

/* Container width */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
    max-width: 780px !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ── Title ── */
.comedybot-title {
    text-align: center;
    margin-bottom: 0.25rem;
}
.comedybot-title h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #FFD700;
    letter-spacing: -0.5px;
    text-shadow: 0 0 40px rgba(255, 215, 0, 0.45), 0 0 80px rgba(255, 180, 0, 0.2);
    margin: 0;
}
.comedybot-title p {
    font-size: 0.82rem;
    color: rgba(255, 215, 0, 0.45);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 4px 0 0 0;
}

/* Divider */
.stage-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(255, 215, 0, 0.15) 20%,
        rgba(255, 215, 0, 0.4) 50%,
        rgba(255, 215, 0, 0.15) 80%,
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
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: rgba(255, 255, 255, 0.04) !important;
    border-color: rgba(255, 255, 255, 0.09) !important;
}

/* Bot bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: rgba(255, 210, 60, 0.05) !important;
    border-color: rgba(255, 210, 60, 0.18) !important;
    box-shadow: 0 0 20px rgba(255, 210, 60, 0.04) !important;
}

/* Message text */
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] {
    color: #EBEBEB !important;
    line-height: 1.65 !important;
    font-size: 0.95rem !important;
}

/* Avatar icons */
[data-testid="stChatMessageAvatarAssistant"] {
    background: rgba(255, 210, 60, 0.15) !important;
    border: 1px solid rgba(255, 210, 60, 0.3) !important;
}
[data-testid="stChatMessageAvatarUser"] {
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
}

/* ── Chat input ── */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.stBottom,
section[data-testid="stBottom"] {
    background: #060606 !important;
    border-top: 1px solid rgba(255, 215, 0, 0.1) !important;
    padding: 12px 0 8px 0 !important;
}

[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 215, 0, 0.25) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(255, 215, 0, 0.6) !important;
    box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.08), 0 0 20px rgba(255, 215, 0, 0.08) !important;
}

[data-testid="stChatInput"] textarea {
    color: #F0F0F0 !important;
    background: transparent !important;
    caret-color: #FFD700 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.25) !important;
}

/* Send button */
[data-testid="stChatInputSubmitButton"] svg {
    fill: rgba(255, 215, 0, 0.7) !important;
}
[data-testid="stChatInputSubmitButton"]:hover svg {
    fill: #FFD700 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 215, 0, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 215, 0, 0.4); }
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
