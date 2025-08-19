import os
import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# --------------------
# Config
# --------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

st.set_page_config(
    page_title="Centi Sage",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------
# Initialize Gemini (if key present)
# --------------------
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.warning(f"⚠️ Gemini init failed: {e}")

# --------------------
# Persistent session state
# --------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm Centi Sage — your AI assistant. Ask me anything.",
            "ts": datetime.utcnow().isoformat(),
        }
    ]

# --------------------
# Custom CSS (navbar + chat bubbles + responsive)
# --------------------
st.markdown(
    """
    <style>
    /* ---------- Navbar ---------- */
    header[data-testid="stHeader"]{display:none}
    .navbar{position:fixed;left:0;right:0;top:0;z-index:999;background:#0b1220;border-bottom:1px solid rgba(255,255,255,0.04);display:flex;align-items:center;justify-content:space-between;padding:10px 22px;color:#fff}
    .navbar .logo{font-weight:700;display:flex;gap:10px;align-items:center}
    .navbar .links{display:flex;gap:12px}
    .navbar .links a{color:#cbd5e1;text-decoration:none;padding:8px 10px;border-radius:8px}
    .navbar .links a:hover{background:#1f2937;color:#fff}

    /* ---------- Layout padding to avoid navbar overlap ---------- */
    .block-container{padding-top:86px !important}

    /* ---------- Chat panel ---------- */
    .chat-panel{display:flex;gap:18px}
    .left-col{width:260px}
    .right-col{flex:1;display:flex;flex-direction:column;height:75vh}

    /* ---------- Message area ---------- */
    .messages{flex:1;overflow:auto;padding:18px;border-radius:12px;background:linear-gradient(180deg,#0f1724 0%, #071027 100%);box-shadow:inset 0 0 0 1px rgba(255,255,255,0.02)}
    .message-row{display:flex;margin-bottom:12px;align-items:flex-end}
    .message-row.user{justify-content:flex-end}
    .bubble{max-width:78%;padding:12px 14px;border-radius:12px;word-wrap:break-word;line-height:1.45;font-size:15px}
    .bubble.ai{background:linear-gradient(180deg,#1f2937,#111827);color:#e6eef8;border-bottom-left-radius:6px}
    .bubble.user{background:#2563eb;color:white;border-bottom-right-radius:6px}
    .meta{font-size:12px;color:rgba(255,255,255,0.5);margin-top:6px}

    /* Avatar */
    .avatar{width:36px;height:36px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;margin-right:10px}
    .avatar.ai{background:#0ea5a4;color:#052022}
    .avatar.user{background:#60a5fa;color:#07203a}

    /* ---------- Input area (sticky) ---------- */
    .input-area{display:flex;gap:12px;padding:12px;border-radius:10px;margin-top:12px;background:transparent}
    .input-box{flex:1}
    .send-btn{padding:10px 14px;border-radius:10px;background:#10b981;color:#fff;border:0}

    /* small screens */
    @media(max-width:880px){
        .left-col{display:none}
        .right-col{height:70vh}
    }
    </style>

    <!-- Scroll helper: ensures messages container auto-scrolls to bottom after new messages -->
    <script>
    const scrollToBottom = () => {
        const el = document.querySelector('.messages');
        if(el){ el.scrollTop = el.scrollHeight; }
    }
    // expose to window so we can call it from Streamlit's rendered HTML updates
    window.scrollToBottom = scrollToBottom;
    </script>
    """,
    unsafe_allow_html=True,
)

# --------------------
# Helper functions
# --------------------

def render_navbar(active="Chat"):
    st.markdown(
        f"""
        <div class="navbar">
          <div class="logo">💬 <span style='font-family:inherit'>Centi Sage</span></div>
          <div class="links">
            <a href="?page=home">Home</a>
            <a href="?page=about">About</a>
            <a href="?page=chat">Chat</a>
            <a href="?page=history">Chat History</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def append_message(role, content):
    st.session_state.messages.append({"role": role, "content": content, "ts": datetime.utcnow().isoformat()})


def generate_reply(prompt_text):
    # If Gemini model is configured, call it. Otherwise return a canned reply to keep UI functional.
    if model:
        try:
            resp = model.generate_content(prompt_text)
            # The generative API returns complex objects — attempt to get `.text` first
            if resp and getattr(resp, "text", None):
                return resp.text
            # As a fallback, try JSON representation
            return str(resp)
        except Exception as e:
            return f"⚠️ Error from API: {e}"
    else:
        return "(Demo) Gemini API key not set. This is a mock reply to show chat flow."

# --------------------
# Pages: Home / About / Chat / History
# --------------------
try:
    params = st.experimental_get_query_params()
    page = params.get("page", ["chat"])[0].lower()
except Exception:
    page = "chat"

render_navbar(page)

if page == "home":
    st.title("🏠 Home — Centi Sage")
    st.write("Welcome — this UI blends ChatGPT-style chat bubbles with features like chat history, file uploads, and export.")

elif page == "about":
    st.title("ℹ️ About")
    st.write("Built with Streamlit and optional Gemini (Google) integration. Paste your GEMINI_API_KEY in a .env file to enable live AI replies.")

elif page == "history":
    st.title("📚 Chat History")
    st.write("Download or clear your saved chat history below.")

    if st.button("Download history (JSON)"):
        st.download_button("Download JSON", data=json.dumps(st.session_state.messages, indent=2), file_name="chat_history.json")

    if st.button("Clear history"):
        st.session_state.messages = []
        st.experimental_rerun()

    # show messages in a dataframe-like view
    import pandas as pd

    if st.session_state.messages:
        df = pd.DataFrame(st.session_state.messages)
        df["ts"] = pd.to_datetime(df["ts"]).dt.tz_localize(None)
        st.dataframe(df.sort_values("ts", ascending=False).reset_index(drop=True))
    else:
        st.info("No messages yet.")

else:  # chat page
    st.markdown("<div class='chat-panel'>", unsafe_allow_html=True)

    # Left column: quick controls
    with st.container():
        cols = st.columns([1, 3])

    left, right = cols

    with left:
        st.markdown("<div class='left-col'>", unsafe_allow_html=True)
        st.markdown("### Controls")
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.experimental_rerun()
        if st.button("Export chat JSON"):
            st.download_button("Download JSON", data=json.dumps(st.session_state.messages, indent=2), file_name="chat_history.json")
        st.markdown("---")
        st.markdown("**Model status**")
        if model:
            st.success("Gemini initialized")
        else:
            st.warning("Gemini not available — UI only")

        st.markdown("---")
        st.markdown("**Upload (image / audio)**")
        uploaded = st.file_uploader("Upload an image or audio to send with your message", type=["png", "jpg", "jpeg", "mp3", "wav"], accept_multiple_files=False)
        if uploaded:
            st.markdown(f"Uploaded: **{uploaded.name}**")
            # store uploaded file reference in session for next message
            st.session_state.upload = uploaded

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='right-col'>", unsafe_allow_html=True)

        # Messages container (will be updated each run)
        messages_html = ["<div class='messages'>"]
        for m in st.session_state.messages:
            role = m.get("role", "assistant")
            ts = m.get("ts", "")
            ts_display = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            if role == "user":
                messages_html.append(
                    f"<div class='message-row user'><div class='bubble user'><div>{st.experimental_escape(m['content'])}</div><div class='meta'>{ts_display}</div></div></div>"
                )
            else:
                messages_html.append(
                    f"<div class='message-row ai'><div class='avatar ai'>AI</div><div class='bubble ai'><div>{st.experimental_escape(m['content'])}</div><div class='meta'>{ts_display}</div></div></div>"
                )
        messages_html.append("</div>")

        st.markdown("".join(messages_html), unsafe_allow_html=True)

        # Call the scroll helper to keep view at bottom after a new message
        st.markdown("<script>window.scrollToBottom()</script>", unsafe_allow_html=True)

        # Input area (text + optional file + send button)
        st.markdown("<div class='input-area'>", unsafe_allow_html=True)
        query = st.text_area("", placeholder="Type your message... (Shift+Enter = newline)", key="input_box", height=80)
        col1, col2 = st.columns([1, 6])
        with col1:
            send = st.button("Send")
        with col2:
            st.markdown("<div style='text-align:right'><small>Tip: You can upload an image/audio on the left. Uploaded file will be referenced in the next message.</small></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # When user sends a message
        if send and query.strip():
            content_to_send = query.strip()

            # If user uploaded a file, attach a simple note (you can expand this to actually send file bytes to the model)
            if st.session_state.get("upload"):
                up = st.session_state.pop("upload")
                content_to_send += f"\n\n[Attached file: {up.name}]"

            append_message("user", content_to_send)

            # Clear input box
            st.session_state["input_box"] = ""

            # Generate reply (sync)
            reply = generate_reply(content_to_send)
            append_message("assistant", reply)

            # Rerun so UI reflects new messages and scrolls
            st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# End of file
