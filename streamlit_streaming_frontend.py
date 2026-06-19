import streamlit as st
from langchain_core.messages import HumanMessage
import uuid

from chat_backend import workflow

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ComedyBot",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def load_conversation_and_return_message_history(id):
    state = workflow.get_state(config={'configurable': {'thread_id': id}})

    temp_messages = []

    for msg in state.values.get('messages', []):
        if isinstance(msg, HumanMessage):
            role = 'user'
        else:
            role = 'assistant'
        temp_messages.append({'role': role, 'content': msg.content})

    return temp_messages

def add_thread_to_history(thread_id):
    if thread_id not in st.session_state["thread_id_history"]:
        st.session_state["thread_id_history"].append(thread_id)

def render_chat():
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_input(prompt: str):
    st.session_state["message_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    final_state = workflow.stream(
        input={"messages": [HumanMessage(content=prompt)]},
        config=CONFIG,
        stream_mode="messages"
    )

    with st.chat_message("assistant"):
        reply = st.write_stream(
            chunk.content for chunk, meta in final_state
        )
    st.session_state["message_history"].append({"role": "assistant", "content": reply})

# ── SESSION STATE INIT ────────────────────────────────────────────────────────

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id_history" not in st.session_state:
    st.session_state["thread_id_history"] = []

add_thread_to_history(st.session_state["thread_id"])

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# ── CALLBACKS ─────────────────────────────────────────────────────────────────

def handle_new_chat_button_click():
    if not st.session_state["message_history"]:
        return
    st.session_state["message_history"] = []
    st.session_state["thread_id"] = str(uuid.uuid4())
    add_thread_to_history(st.session_state["thread_id"])


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

st.sidebar.button("New Chat", on_click=handle_new_chat_button_click)
st.sidebar.header("Conversation History")

for thread_id in st.session_state["thread_id_history"]:
    if st.sidebar.button(thread_id[:23]):
        st.session_state["thread_id"] = thread_id
        st.session_state["message_history"] = load_conversation_and_return_message_history(thread_id)



# ── MAIN PAGE ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="comedybot-title">
    <h1>🎤 ComedyBot</h1>
    <p>Stand-up comedian · powered by AI · zero chill</p>
</div>
<hr class="stage-divider">
""", unsafe_allow_html=True)

render_chat()

# ── INPUT ─────────────────────────────────────────────────────────────────────

user_input = st.chat_input("Say something... I dare you 🎤")
if user_input:
    handle_input(user_input)
