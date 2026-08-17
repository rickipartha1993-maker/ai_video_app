
import streamlit as st
import requests
import re

# Streamlit Page Configuration
st.set_page_config(page_title="AI Video Short Generator Suite", page_icon="🎬", layout="wide")

# Secrets Load
try:
    RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
except Exception:
    RAPIDAPI_KEY = ""

try:
    MASTER_PASSWORD = st.secrets["DEVELOPER_MASTER_PASSWORD"]
except Exception:
    MASTER_PASSWORD = "NI19la93@18"

if not RAPIDAPI_KEY:
    st.error("Error: RAPIDAPI_KEY is missing. Configure it in Streamlit Cloud settings.")
    st.stop()

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.is_developer = False

# Sidebar Login
st.sidebar.header("🔐 Access Control")
if not st.session_state.logged_in:
    email = st.sidebar.text_input("Enter Email:")
    if st.sidebar.button("Login"):
        if email and "@" in email:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
    st.sidebar.markdown("---")
    pwd = st.sidebar.text_input("Developer Password:", type="password")
    if st.sidebar.button("Developer Login"):
        if pwd == MASTER_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.is_developer = True
            st.session_state.user_email = "developer@admin.com"
            st.rerun()
    st.stop()

# --- Main App ---
st.title("🎬 AI Script-to-Video & Short Generator Suite")
youtube_url = st.text_input("Enter YouTube Video URL:", "")

def get_video_download_url(yt_url):
    # Link Normalizer: youtu.be/ID -> youtube.com/watch?v=ID
    if "youtu.be" in yt_url:
        video_id = yt_url.split("/")[-1].split("?")[0]
        yt_url = f"https://www.youtube.com/watch?v={video_id}"
    
    url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
    headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"}
    response = requests.get(url, headers=headers, params={"url": yt_url})
    
    if response.status_code == 200:
        data = response.json()
        # API Response structure check
        if 'links' in data:
            return data['links'][0]['url'] if isinstance(data['links'], list) else list(data['links'].values())[0]
    return None

if st.button("🚀 Start Video & Shorts Processing"):
    if not youtube_url:
        st.warning("Please provide a valid YouTube URL.")
    else:
        with st.spinner("Processing..."):
            video_link = get_video_download_url(youtube_url)
            if video_link:
                st.success("Success!")
                st.markdown(f"📥 [Download Your Video]({video_link})")
            else:
                st.error("Failed to process the URL. The API might not support this specific video or the link is invalid.")

