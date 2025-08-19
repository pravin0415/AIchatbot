import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

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

# ---------- Inject custom CSS ----------
st.markdown("""
    <style>
    /* Hide default Streamlit header (where Share/GitHub appear) */
    header[data-testid="stHeader"] {
        display: none;
    }
    /* Push navbar on top */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #111;
        border-bottom: 1px solid #333;
        padding: 12px 20px;
    }
    .navbar-logo {
        color:#f5f5f5;
        font-weight:600;
        font-size:18px;
    }
    .navbar-links {
        display:flex;
        gap:18px;
    }
    .navbar-links a {
        text-decoration:none;
        color:#e5e5e5;
        font-weight:500;
        padding:8px 12px;
        border-radius:6px;
        transition:0.25s;
    }
    .navbar-links a:hover { background:#2563eb;color:#fff; }
    .navbar-links a.active { background:#1e3a8a;color:#fff; }

    /* Mobile toggle */
    .navbar-toggle {
        display:none;
        font-size:22px;
        color:#f5f5f5;
        cursor:pointer;
    }
    #nav-toggle { display:none; }
    .navbar-menu {
        display:none;
        flex-direction:column;
        gap:10px;
        background:#111;
        padding:10px 20px;
    }
    @media(max-width:768px){
        .navbar-links{display:none;}
        .navbar-toggle{display:block;}
        #nav-toggle:checked ~ .navbar-menu{display:flex;}
        .navbar-menu a{
            padding:10px;
            color:#e5e5e5;
            text-decoration:none;
            border-radius:6px;
        }
        .navbar-menu a:hover{background:#2563eb;color:#fff;}
    }

    /* Push all page content below navbar */
    .block-container {
        padding-top: 80px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Gemini init ----------
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        st.error(f"⚠️ Could not initialize Gemini: {e}")

# ---------- Read current page ----------
try:
    params = st.query_params
    page = params.get("page", "chat")
except Exception:
    params = st.experimental_get_query_params()
    page = params.get("page", ["chat"])[0]

page = (page or "chat").lower()

# ---------- Navbar ----------
def navbar(active_page: str):
    def cls(name): return "active" if active_page == name else ""

    st.markdown(f"""
    <div class="navbar">
      <div class="navbar-logo">💬 ChatGPT Clone</div>
      <div class="navbar-links">
        <a class="{cls('home')}" href="?page=home">Home</a>
        <a class="{cls('about')}" href="?page=about">About</a>
        <a class="{cls('chat')}" href="?page=chat">Chat</a>
        <a class="{cls('login')}" href="?page=login">Login/Register</a>
      </div>
      <label for="nav-toggle" class="navbar-toggle">☰</label>
    </div>
    <input type="checkbox" id="nav-toggle" />
    <div class="navbar-menu">
      <a class="{cls('home')}" href="?page=home">Home</a>
      <a class="{cls('about')}" href="?page=about">About</a>
      <a class="{cls('chat')}" href="?page=chat">Chat</a>
      <a class="{cls('login')}" href="?page=login">Login/Register</a>
    </div>
    """, unsafe_allow_html=True)

navbar(page)

# ---------- Pages ----------
if page == "home":
    st.title("🏠 Home")
    st.write("Welcome to the ChatGPT-style clone.")

elif page == "about":
    st.title("ℹ️ About")
    st.write("Built with **Streamlit + Gemini API** and custom CSS for mobile-friendly chat.")

elif page == "chat":
    st.markdown("<h1 class='app-title'>💬 Chat</h1>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI assistant. How can I help you today?"}
        ]

    # Show history
    for msg in st.session_state.messages:
        role_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
        st.markdown(f"<div class='{role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"<div class='user-bubble'>{prompt}</div>", unsafe_allow_html=True)

        if model:
            try:
                resp = model.generate_content(prompt)
                reply = resp.text if resp and getattr(resp, "text", None) else "⚠️ No response."
            except Exception as e:
                reply = f"⚠️ Error: {e}"
        else:
            reply = "⚠️ No API key set. (UI works, but AI replies are disabled)"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.markdown(f"<div class='ai-bubble'>{reply}</div>", unsafe_allow_html=True)

elif page == "login":
    st.title("🔑 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Login"):
            if u and p:
                st.success(f"✅ Welcome back, {u}!")
            else:
                st.error("⚠️ Enter username and password.")
    with tab2:
        u2 = st.text_input("New Username", key="reg_u")
        p2 = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Register"):
            if u2 and p2:
                st.success(f"🎉 Account created for {u2}!")
            else:
                st.error("⚠️ Enter username and password.")
