
import streamlit as st
import requests
from streamlit_lottie import st_lottie
import os
from yt_dlp import YoutubeDL
from PIL import Image, ImageDraw

# Page Config
st.set_page_config(page_title="Video Short Generator", page_icon="🎬", layout="centered")

# Lottie Animation (Auto Video Editing/Shorts Theme)
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# Pre-configured animation matching video/content creation theme
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json"
lottie_json = load_lottieurl(lottie_url)

# Session State
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "dev_mode" not in st.session_state: st.session_state.dev_mode = False

# Developer Access
st.sidebar.subheader("Developer Access")
is_dev = st.sidebar.checkbox("I am a Developer")
if is_dev:
    dev_pass = st.sidebar.text_input("Enter Dev Password:", type="password")
    if dev_pass == "NI19la93@18":
        st.session_state.dev_mode = True
        st.session_state.authenticated = True
        st.rerun()

# Login Page with Auto-loaded Animation and Images
def login_page():
    st.markdown("<h1 style='text-align: center;'>Video Short Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Professional AI-powered video editing tool.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if lottie_json:
            st_lottie(lottie_json, height=280, key="login_anim")
    with col2:
        # Automatically included relevant video production stock image
        st.image("https://images.unsplash.com/photo-1574943320219-555621f57d6e?auto=format&fit=crop&q=80&w=400", caption="Transform Long Videos into Viral Shorts")
        
    st.markdown("---")
    st.markdown("### Sign In to Get Started")
    email = st.text_input("Enter your Gmail")
    if st.button("Access Dashboard"):
        if email and "@gmail.com" in email:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Please enter a valid Gmail address.")
    st.stop()

# Main App
def main_app():
    st.title("Dashboard")
    st.write("You are logged in successfully.")
    
if not st.session_state.authenticated:
    login_page()
else:
    main_app()

