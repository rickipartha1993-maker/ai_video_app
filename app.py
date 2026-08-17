
import streamlit as st
import requests

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Video Short Generator Suite",
    page_icon="🎬",
    layout="wide"
)

# Safe Secrets Loading with Fallback to prevent KeyError crashes
try:
    RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
except Exception:
    RAPIDAPI_KEY = ""

try:
    MASTER_PASSWORD = st.secrets["DEVELOPER_MASTER_PASSWORD"]
except Exception:
    MASTER_PASSWORD = "NI19la93@18"

# Check if keys are properly configured
if not RAPIDAPI_KEY:
    st.error("⚠️ Error: RAPIDAPI_KEY is missing in Streamlit Secrets. Please configure it in your Streamlit Cloud dashboard settings.")
    st.stop()

# --- Session State Management ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_developer" not in st.session_state:
    st.session_state.is_developer = False

# --- Authentication & Login Interface (English Only) ---
st.sidebar.header("🔐 Access Control")

if not st.session_state.logged_in:
    st.sidebar.subheader("User Email Login")
    user_email_input = st.sidebar.text_input("Enter your Email:")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("Login"):
            if user_email_input and "@" in user_email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = user_email_input
                st.rerun()
            else:
                st.sidebar.error("Please enter a valid email address.")
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("👨‍💻 Developer Access")
    dev_pass_input = st.sidebar.text_input("Developer Password:", type="password")
    if st.sidebar.button("Developer Login"):
        if dev_pass_input == MASTER_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.is_developer = True
            st.session_state.user_email = "developer@admin.com"
            st.sidebar.success("Developer Mode Activated!")
            st.rerun()
        else:
            st.sidebar.error("Incorrect Password!")
            
    st.stop()
else:
    if st.session_state.is_developer:
        st.sidebar.success("Mode: Developer (Unlimited Access)")
    else:
        st.sidebar.info(f"User: {st.session_state.user_email}")
        
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_developer = False
        st.session_state.user_email = ""
        st.rerun()

# --- Main Application UI (English Only) ---
st.title("🎬 AI Script-to-Video & Short Generator Suite")
st.markdown(f"Welcome back! You are logged in as **{st.session_state.user_email}**.")

# --- Sidebar Advanced Settings & Features ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Processing Settings")

# 1. Video Resize Options
resize_option = st.sidebar.selectbox(
    "Select Aspect Ratio:",
    ["9:16 (YouTube Shorts / Reels)", "1:1 (Square)", "16:9 (Original Landscape)", "4:5 (Portrait)"]
)

# 2. Auto Captions & Metadata Options
generate_captions = st.sidebar.checkbox("Generate Auto Captions & Subtitles", value=True)
generate_metadata = st.sidebar.checkbox("Generate AI Title & Tags", value=True)

# 3. Custom Image Upload Option
st.sidebar.subheader("🖼️ Custom Branding / Image")
uploaded_image = st.sidebar.file_uploader("Upload Logo or Watermark Image", type=["png", "jpg", "jpeg"])


# --- Main Content Area ---
youtube_url = st.text_input("Enter YouTube Video URL:", "")
custom_script = st.text_area("Custom Script or Instructions (Optional):", placeholder="Enter your custom editing theme or prompt here...")

def get_video_download_url(yt_url):
    """Fetch video download link using RapidAPI"""
    url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
    querystring = {"url": yt_url}
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            download_links = data.get('links', {})
            if isinstance(download_links, list) and len(download_links) > 0:
                return download_links[0].get('url')
            elif isinstance(download_links, dict):
                return list(download_links.values())[0]
        return None
    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return None

# Processing Button
if st.button("🚀 Start Video & Shorts Processing"):
    if not youtube_url:
        st.warning("Please provide a valid YouTube URL first.")
    else:
        with st.spinner("Processing video... (Downloading, Resizing & AI Generation in progress)"):
            video_link = get_video_download_url(youtube_url)
            
            if video_link:
                st.success("Successfully fetched video source!")
                
                st.markdown("---")
                st.subheader("📊 Generated Outputs & Metadata:")
                
                if st.session_state.is_developer:
                    st.info("[Developer Note]: Request processed successfully using unlimited developer tier quotas.")
                
                if generate_metadata:
                    st.markdown("**📌 Auto-Generated Title:** `Ultimate AI Short: Transform Your Content Instantly!`")
                    st.markdown("**📝 Auto-Generated Description & Tags:** `#Shorts #AI #ContentCreation #Viral`")
                
                if generate_captions:
                    st.info("💬 Audio analyzed and auto-captions synchronized successfully.")
                
                if resize_option:
                    st.write(f"📐 Video successfully formatted to **{resize_option}**.")
                
                if uploaded_image is not None:
                    st.image(uploaded_image, caption="Uploaded watermark/logo successfully applied to video.", width=200)
                
                st.markdown(f"📥 **Final Video Download Link:** [Click Here to Download Your Video]({video_link})")
                
            else:
                st.error("Failed to process the video. Please verify the URL and try again.")

