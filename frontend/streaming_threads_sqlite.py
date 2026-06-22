import streamlit as st
from langchain_core.messages import HumanMessage
import uuid

from backend.chat_database_backend import workflow, get_all_unique_threads_from_state

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ComedyBot",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def load_conversation_and_return_message_history(id):
    # Notice that we are fetching the state of the thread which is being clicked.
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
    if thread_id not in st.session_state["past_conversations_thread_id"]:
        st.session_state["past_conversations_thread_id"].append(thread_id)

def render_chat():
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_input(prompt: str):
    st.session_state["message_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    config = {"configurable": {"thread_id": st.session_state["thread_id"]},
              "metadata": {"thread_id": st.session_state["thread_id"]}
              }

    final_state = workflow.stream(
        input={"messages": [HumanMessage(content=prompt)]},
        config=config,
        stream_mode="messages"
    )
    # Function inside a function
    def _stream_chunks():
        try:
            for chunk, meta in final_state:
                yield chunk.content
        except GeneratorExit:
            pass

    with st.chat_message("assistant"):
        reply = st.write_stream(_stream_chunks())
    st.session_state["message_history"].append({"role": "assistant", "content": reply})

# ── SESSION STATE INIT ────────────────────────────────────────────────────────

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "past_conversations_thread_id" not in st.session_state:
    st.session_state["past_conversations_thread_id"] = get_all_unique_threads_from_state()

# Adding the current thread to history as well to be rendered
add_thread_to_history(st.session_state["thread_id"])



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

for thread_id in st.session_state["past_conversations_thread_id"]:
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
