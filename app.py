
import streamlit as st
import requests
from streamlit_lottie import st_lottie

# Page Config
st.set_page_config(page_title="Video Short Generator", page_icon="🎬", layout="centered")

# Initialize Session State
if "authenticated" not in st.session_state: 
    st.session_state.authenticated = False
if "dev_mode" not in st.session_state: 
    st.session_state.dev_mode = False
if "user_email" not in st.session_state: 
    st.session_state.user_email = ""

# Lottie Animation Loader
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

lottie_url = "https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json"
lottie_json = load_lottieurl(lottie_url)

# ----------------- DEVELOPER ACCESS (Sidebar) -----------------
st.sidebar.subheader("Developer Access")
is_dev = st.sidebar.checkbox("I am a Developer")
if is_dev:
    dev_pass = st.sidebar.text_input("Enter Dev Password:", type="password")
    if dev_pass == "NI19la93@18":
        st.session_state.dev_mode = True
        st.session_state.authenticated = True
        st.sidebar.success("Developer Mode Active!")

# ----------------- LOGIN PAGE (For Users) -----------------
def login_page():
    st.markdown("<h1 style='text-align: center;'>Video Short Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Professional AI-powered video editing tool.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_json:
            st_lottie(lottie_json, height=250, key="login_anim")
    with col2:
        st.write("### Welcome")
        st.write("Transform long videos into viral shorts instantly.")
        
        email = st.text_input("Enter your Gmail")
        if st.button("Access Dashboard"):
            if email and "@gmail.com" in email:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter a valid Gmail address.")
    st.stop()

# ----------------- MAIN APP DASHBOARD -----------------
def main_app():
    if st.session_state.dev_mode:
        st.sidebar.success("Mode: Developer (Unlimited)")
    else:
        st.sidebar.info(f"User: {st.session_state.user_email}")
        if st.sidebar.button("Log Out"):
            st.session_state.authenticated = False
            st.session_state.dev_mode = False
            st.rerun()

    st.title("🎬 Dashboard - Video Generator")
    st.write("Welcome to the main tool! You have successfully accessed the application.")
    
    # Your video processing and editing tools will go here
    video_url = st.text_input("Enter Video Link:")
    if st.button("Process Video"):
        if video_url:
            st.success("Video processing simulation started successfully!")
        else:
            st.error("Please provide a video link.")

# ----------------- ROUTING FLOW -----------------
if not st.session_state.authenticated:
    login_page()
else:
    main_app()

