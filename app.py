
import os
import streamlit as st
from moviepy.editor import VideoFileClip
import yt_dlp
import urllib.parse

# Page configuration
st.set_page_config(page_title="Video Short & Metadata Generator", page_icon="🎥", layout="centered")

st.title("🎥 Video Short Generator & Auto Metadata")
st.write("Paste any long video link, create short clips, remove watermarks, and get auto-generated titles and descriptions!")

# Session state tracking
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0

if 'is_subscribed' not in st.session_state:
    st.session_state.is_subscribed = False

# ==========================================
# 👑 Developer Bypass / Admin Section
# ==========================================
st.sidebar.title("🛠️ Developer Panel")
dev_mode = st.sidebar.checkbox("I am the App Developer (Free & Unlimited Access)")

if dev_mode:
    dev_pass = st.sidebar.text_input("Enter Developer Password:", type="password")
    if dev_pass == "NI19la93@18":
        st.sidebar.success("Admin access granted! No subscription needed.")
        st.session_state.is_subscribed = True
    elif dev_pass != "":
        st.sidebar.error("Incorrect password!")

# ==========================================
# 📤 App Sharing Interface (Sidebar Share Section)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.title("📤 Share This App")
st.sidebar.write("Share this amazing app with your friends and colleagues:")

# Replace with your actual live Streamlit app URL if needed
app_link = "https://alvideoapp-8joyèykrvfdutpuacjok9p.streamlit.app"
share_message = f"🔥 Check out this awesome Video Short Generator app! Create clips and remove watermarks instantly: {app_link}"
encoded_message = urllib.parse.quote(share_message)
whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_message}"

st.sidebar.markdown(
    f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">📲 Share on WhatsApp</button></a>',
    unsafe_allow_html=True
)

FREE_LIMIT = 2

# Freemium Limit Check
if st.session_state.video_count >= FREE_LIMIT and not st.session_state.is_subscribed:
    st.warning("⚠️ Your free trial limit (2 videos) has been reached! Choose a subscription plan below or enable developer mode from the sidebar to continue.")
    
    st.markdown("---")
    st.subheader("💎 Premium Subscription Plans")
    st.write("Choose a plan for regular usage:")

    plan_choice = st.radio(
        "Select your plan:",
        (
            "Daily Pass - ₹19 / Day",
            "Monthly Pro - ₹299 / Month",
            "Yearly Mega - ₹1,999 / Year"
        )
    )

    st.markdown("---")
    st.write("### 💳 Payment Options (UPI / PayTM / BharatPe / Razorpay)")
    payment_method = st.selectbox(
        "Select payment method:",
        ["UPI (Google Pay / PhonePe / Paytm)", "Paytm Wallet", "BharatPe QR / Net Banking", "Credit / Debit Card (Razorpay)"]
    )

    if st.button("Complete Payment & Subscribe"):
        st.session_state.is_subscribed = True
        st.success(f"Thank you! You have successfully subscribed to the '{plan_choice}'.")
        st.rerun()
        
    st.stop()

# Video Link Input
video_url = st.text_input("Enter Video Link (e.g., YouTube Link):", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Generate & Process Video"):
    if video_url:
        try:
            st.info("Downloading and processing video from the link...")
            
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': 'downloaded_video.mp4',
                'merge_output_format': 'mp4',
            }
            
            video_title = "Awesome YouTube Short"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_title = info_dict.get('title', 'YouTube Short')
                
            st.success("Video downloaded successfully!")
            
            video_path = "downloaded_video.mp4"
            clip = VideoFileClip(video_path)
            
            w, h = clip.size
            cropped_clip = clip.crop(x1=int(w*0.05), y1=int(h*0.05), x2=int(w*0.95), y2=int(h*0.95))
            
            short_clip = cropped_clip.subclip(0, min(30, cropped_clip.duration))
            output_path = "output_short.mp4"
            
            short_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                bitrate="5000k",
                preset="medium"
            )
            
            st.video(output_path)
            st.success("Short video created successfully with watermark removed!")
            
            st.subheader("🤖 Auto-Generated Metadata (Title & Description)")
            gen_title = f"🔥 {video_title[:50]}... #Shorts #Viral"
            gen_description = f"Watch this amazing moment from the video! Don't forget to like, share and subscribe for more shorts.\n\nOriginal Source: {video_url}\n\n#Shorts #Trending #YouTubeShorts #ViralVideo"
            
            st.markdown(f"**📌 Title:**")
            st.code(gen_title, language="text")
            
            st.markdown(f"**📝 Description:**")
            st.code(gen_description, language="text")
            
            if not dev_mode:
                st.session_state.video_count += 1
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid video link!")

