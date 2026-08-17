
import streamlit as st
import requests
from streamlit_lottie import st_lottie
import os
import subprocess
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image

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
    st.write("Configure your target platform, upload custom graphics, and process your video.")
    
    # 1. Video Link Input
    video_url = st.text_input("Enter YouTube Video Link:")
    
    # 2. Platform & Resolution Selection
    st.markdown("### 📱 Select Target Platform & Size")
    platform = st.selectbox(
        "Choose where you want to upload:",
        [
            "YouTube Shorts / TikTok / Instagram Reels (9:16 - 1080x1920)",
            "Facebook Feed / Standard Video (16:9 - 1920x1080)",
            "Instagram Square Post (1:1 - 1080x1080)"
        ]
    )
    
    # 3. Custom Image/Logo Overlay Feature
    st.markdown("### 🖼️ Custom Overlay Image / Logo")
    uploaded_image = st.file_uploader("Upload your image or logo to overlay on video (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if st.button("Process & Generate Video"):
        if video_url:
            with st.spinner("Updating yt-dlp and downloading video... Please wait."):
                try:
                    # Auto-upgrade yt-dlp to fix 403 Forbidden errors
                    subprocess.run(["pip", "install", "--upgrade", "yt-dlp"], check=False)

                    ydl_opts = {
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': 'downloaded_video.mp4',
                        'geo_bypass': True,
                    }
                    
                    if os.path.exists("downloaded_video.mp4"):
                        os.remove("downloaded_video.mp4")
                        
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                        
                    st.success("Video downloaded successfully. Processing formatting & overlay...")
                    
                    # Load video via MoviePy
                    clip = VideoFileClip("downloaded_video.mp4")
                    
                    # Resize/Crop based on selected platform
                    w, h = clip.size
                    if "9:16" in platform:
                        # Crop center for vertical shorts
                        target_w = int(h * (9 / 16))
                        if target_w < w:
                            x_center = w / 2
                            clip = clip.crop(x1=x_center - target_w/2, y1=0, x2=x_center + target_w/2, y2=h)
                        clip = clip.resize(height=1920)
                    elif "1:1" in platform:
                        # Square crop
                        min_dim = min(w, h)
                        clip = clip.crop(x1=(w - min_dim)/2, y1=(h - min_dim)/2, x2=(w + min_dim)/2, y2=(h + min_dim)/2)
                        clip = clip.resize(width=1080)
                    else:
                        # 16:9 standard
                        clip = clip.resize(width=1920)

                    # Handle Custom Image Overlay if uploaded
                    if uploaded_image is not None:
                        img_path = "user_overlay_img.png"
                        with open(img_path, "wb") as f:
                            f.write(uploaded_image.getbuffer())
                        
                        logo = ImageClip(img_path).set_duration(clip.duration).resize(height=120).set_position(("right", "top"))
                        final_clip = CompositeVideoClip([clip, logo])
                    else:
                        final_clip = clip

                    # Export output video
                    output_file = "final_output.mp4"
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        
                    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, preset="fast")
                    
                    st.success("Video processed and formatted successfully!")
                    st.video(output_file)
                        
                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
        else:
            st.error("Please provide a valid video link.")

# ----------------- ROUTING FLOW -----------------
if not st.session_state.authenticated:
    login_page()
else:
    main_app()

