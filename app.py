import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import html

# ---------- Config ----------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

st.set_page_config(
    page_title="ChatGPT Clone",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
st.markdown("""
<style>
/* Navbar */
.navbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 60px;
    background: white;
    border-bottom: 1px solid #e0e0e0;
    display: flex; align-items: center;
    padding: 0 20px;
    font-weight: 600;
    z-index: 1000;
}

/* Page container fix */
.block-container {
    padding-top: 80px !important;
}

/* Chat styling */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 10px;
}

.message-row {
    display: flex;
    width: 100%;
}

.message-row.user {
    justify-content: flex-end;
}

.bubble {
    max-width: 80%;
    padding: 10px 14px;
    border-radius: 16px;
    word-wrap: break-word;
    font-size: 15px;
    line-height: 1.4;
}

.bubble.user {
    background: #007AFF;
    color: white;
    border-bottom-right-radius: 4px;
}

.bubble.ai {
    background: #f2f2f2;
    color: black;
    border-bottom-left-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Navbar ----------
st.markdown("<div class='navbar'>💬 ChatGPT Clone</div>", unsafe_allow_html=True)

# ---------- Chat State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- Gemini Setup ----------
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
else:
    model = None

# ---------- Chat UI ----------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    content = html.escape(msg["content"])
    if role == "user":
        st.markdown(f"<div class='message-row user'><div class='bubble user'>{content}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message-row ai'><div class='bubble ai'>{content}</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------- Input ----------
if prompt := st.chat_input("Type your message..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI response
    if model:
        try:
            response = model.generate_content(prompt)
            reply = response.text
        except Exception as e:
            reply = "⚠️ Error connecting to AI."
    else:
        reply = "⚠️ Gemini API key not set. Showing mock response."

    st.session_state.messages.append({"role": "ai", "content": reply})
    st.experimental_rerun()


