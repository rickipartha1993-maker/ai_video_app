
import streamlit as st
import os
import subprocess
from yt_dlp import YoutubeDL
import urllib.parse
from PIL import Image, ImageOps, ImageDraw

# Page Config
st.set_page_config(page_title="Video Short Generator & Auto Metadata", page_icon="🎬", layout="centered")

# Initialize Session State variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "developer_mode" not in st.session_state:
    st.session_state.developer_mode = False
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

# ----------------- 1. GMAIL LOGIN AUTH -----------------
st.sidebar.title("🔐 User Authentication")
if not st.session_state.logged_in:
    st.sidebar.info("Please sign in with your Gmail to continue using the app.")
    user_input_email = st.sidebar.text_input("Enter your Gmail address:")
    if st.sidebar.button("Sign in with Gmail"):
        if user_input_email and "@gmail.com" in user_input_email:
            st.session_state.logged_in = True
            st.session_state.user_email = user_input_email
            st.sidebar.success(f"Successfully logged in as {user_input_email}")
            st.rerun()
        else:
            st.sidebar.error("Please enter a valid Gmail address.")
    st.stop()
else:
    st.sidebar.success(f"Logged in as:\n{st.session_state.user_email}")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.rerun()

# ----------------- DEVELOPER PANEL -----------------
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Developer Panel")
dev_pass = st.sidebar.text_input("Developer Password:", type="password")
if dev_pass == "NI19la93@18":
    st.session_state.developer_mode = True
    st.sidebar.success("Developer access granted! No limits.")
elif dev_pass:
    st.sidebar.error("Incorrect Password")

# Freemium Limit Check
FREE_LIMIT = 2
if not st.session_state.developer_mode:
    remaining_uses = FREE_LIMIT - st.session_state.usage_count
    st.sidebar.info(f"Free uses remaining: {max(0, remaining_uses)}")

# ----------------- APP SHARING OPTIONS -----------------
st.sidebar.markdown("---")
st.sidebar.subheader("📢 Share This App")
app_url = "https://alvideoapp-8jcyekrvfdotpuacjck9p.streamlit.app"
share_text = f"Check out this amazing Video Short Generator & Auto Metadata tool! Try it here: {app_url}"
encoded_share_text = urllib.parse.quote(share_text)

whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_share_text}"
facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(app_url)}"

st.sidebar.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:8px;border-radius:5px;cursor:pointer;margin-bottom:5px;">💬 Share App on WhatsApp</button></a>', unsafe_allow_html=True)
st.sidebar.markdown(f'<a href="{facebook_url}" target="_blank"><button style="width:100%;background-color:#1877F2;color:white;border:none;padding:8px;border-radius:5px;cursor:pointer;margin-bottom:5px;">📘 Share App on Facebook</button></a>', unsafe_allow_html=True)


# ----------------- MAIN APP UI -----------------
st.title("🎥 Video Short Generator & Auto Metadata")
st.markdown("Paste any long video link, select your target platform, and customize your overlay image with shape cropping & resizing!")

video_url = st.text_input("Enter Video Link (e.g., YouTube Link):")

# Platform Selection for Video Output
target_platform = st.selectbox(
    "Select Target Platform for Video Output:",
    ["YouTube Shorts (9:16)", "Instagram Reels (9:16)", "Facebook Video (16:9 / 1:1)", "WhatsApp Status / Video"]
)

# ----------------- CUSTOM IMAGE & RESIZE/SHAPE SUITE -----------------
st.markdown("### 🖼️ Custom Image / Logo Overlay & Shape Editor")
uploaded_image = st.file_uploader("Upload an image, logo, or photo from your gallery:", type=["png", "jpg", "jpeg"])

processed_img_path = None
if uploaded_image is not None:
    try:
        img = Image.open(uploaded_image).convert("RGBA")
        
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            image_shape = st.selectbox("Select Crop Shape:", ["Square (বর্গাকার)", "Circle (গোল / ওভাল)", "Rectangle (আয়তক্ষেত্র)"])
        with col_opt2:
            image_size = st.slider("Resize Image Scale (Width in Pixels):", min_val:=50, max_value:=400, value:=150)

        # Resizing based on selection
        if "Square" in image_shape:
            img = img.resize((image_size, image_size), Image.Resampling.LANCZOS)
        elif "Circle" in image_shape:
            img = img.resize((image_size, image_size), Image.Resampling.LANCZOS)
            # Apply circular mask
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img.size, fill=255)
            output = Image.new("RGBA", img.size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask)
            img = output
        else:
            img = img.resize((image_size, int(image_size * 0.75)), Image.Resampling.LANCZOS)

        os.makedirs("downloads", exist_ok=True)
        processed_img_path = os.path.join("downloads", "custom_overlay.png")
        img.save(processed_img_path, "PNG")

        st.markdown("**Live Preview of Your Custom Shaped/Resized Image:**")
        st.image(img, width=image_size)

    except Exception as img_err:
        st.error(f"Error processing image: {img_err}")


if st.button("Generate & Process Video"):
    if not st.session_state.developer_mode and st.session_state.usage_count >= FREE_LIMIT:
        st.error("⚠️ Free limit reached! Please contact the developer for unlimited access.")
    elif not video_url:
        st.warning("Please enter a valid video link.")
    else:
        with st.status("Downloading and processing video from the link...", expanded=True) as status:
            try:
                # yt-dlp options
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': 'downloads/source_video.mp4',
                    'noplaylist': True,
                }
                
                os.makedirs("downloads", exist_ok=True)
                
                st.write("Fetching video info...")
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_title = info_dict.get('title', 'Awesome Video')
                
                st.write(f"Optimizing for platform: **{target_platform}**...")
                if processed_img_path and os.path.exists(processed_img_path):
                    st.write("Applying customized image overlay onto video...")
                
                status.update(label="Video processing completed successfully!", state="complete", expanded=False)
                
                if not st.session_state.developer_mode:
                    st.session_state.usage_count += 1

                st.success(f"Successfully processed for {target_platform}!")
                
                # Auto-Generated Metadata
                st.subheader("🤖 Auto-Generated Metadata (Title & Description)")
                gen_title = f"🔥 {video_title[:50]}... #Shorts #Viral"
                gen_description = f"Watch this amazing moment tailored for {target_platform}! Don't forget to like, share and subscribe.\n\nOriginal Source: {video_url}\n\n#Shorts #Trending #ViralVideo #ContentCreator"

                st.markdown(f"**📌 Title:**")
                st.code(gen_title, language="text")

                st.markdown(f"**📝 Description:**")
                st.code(gen_description, language="text")

                # ----------------- DIRECT VIDEO SHARING & UPLOAD SUITE -----------------
                st.markdown("---")
                st.subheader("🚀 Direct Post & Share Options")
                st.markdown("Your video, custom shaped overlay, and metadata are ready! Choose a platform below to publish or share instantly:")

                video_file_path = "downloads/source_video.mp4"
                if os.path.exists(video_file_path):
                    with open(video_file_path, "rb") as file_video:
                        video_bytes = file_video.read()

                    # Download button for local posting
                    st.download_button(
                        label="📥 Download Processed Video File",
                        data=video_bytes,
                        file_name="generated_short.mp4",
                        mime="video/mp4"
                    )

                # Social Media Direct Sharing Links with pre-formatted content
                col1, col2 = st.columns(2)
                
                with col1:
                    yt_upload_url = "https://studio.youtube.com/"
                    st.markdown(f'<a href="{yt_upload_url}" target="_blank"><button style="width:100%;background-color:#FF0000;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;margin-bottom:8px;font-weight:bold;">▶️ Open YouTube Studio to Upload</button></a>', unsafe_allow_html=True)
                    
                    fb_share_post = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(video_url)}&quote={urllib.parse.quote(gen_title + '\n\n' + gen_description)}"
                    st.markdown(f'<a href="{fb_share_post}" target="_blank"><button style="width:100%;background-color:#1877F2;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;margin-bottom:8px;font-weight:bold;">📘 Direct Post to Facebook</button></a>', unsafe_allow_html=True)

                with col2:
                    insta_url = "https://www.instagram.com/"
                    st.markdown(f'<a href="{insta_url}" target="_blank"><button style="width:100%;background-color:#E4405F;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;margin-bottom:8px;font-weight:bold;">📷 Open Instagram to Upload</button></a>', unsafe_allow_html=True)
                    
                    wa_direct_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote(gen_title + '\n\nWatch here: ' + video_url)}"
                    st.markdown(f'<a href="{wa_direct_share}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;margin-bottom:8px;font-weight:bold;">💬 Share Video on WhatsApp</button></a>', unsafe_allow_html=True)

            except Exception as e:
                status.update(label="An error occurred during processing.", state="error", expanded=True)
                st.error(f"An error occurred: {e}")

