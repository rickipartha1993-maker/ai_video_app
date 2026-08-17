
import os
import streamlit as st
from moviepy.editor import VideoFileClip
import yt_dlp

# Page configuration
st.set_page_config(page_title="Video Short & Metadata Generator", page_icon="🎥", layout="centered")

st.title("🎥 Video Short Generator & Auto Metadata")
st.write("যে কোনো লং ভিডিওর লিংক দিন, শর্ট ক্লিপ তৈরি করুন, ওয়াটারমার্ক রিমুভ করুন এবং অটো টাইটেল-ডেসক্রিপশন পান!")

# সেশন স্টেট (Session State) ট্র্যাকিং
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0

if 'is_subscribed' not in st.session_state:
    st.session_state.is_subscribed = False

# ==========================================
# 👑 ডেভেলপার বাইপাস / অ্যাডমিন সেকশন
# ==========================================
st.sidebar.title("🛠️ Developer Panel")
dev_mode = st.sidebar.checkbox("আমি অ্যাপ ডেভেলপার (Free & Unlimited Access)")

if dev_mode:
    dev_pass = st.sidebar.text_input("ডেভেলপার পাসওয়ার্ড দিন:", type="password")
    if dev_pass == "NI19la93@18":
        st.sidebar.success("অ্যাডমিন এক্সেস সফল! আপনার কোনো সাবস্ক্রিপশন লাগবে না।")
        st.session_state.is_subscribed = True
    elif dev_pass != "":
        st.sidebar.error("ভুল পাসওয়ার্ড!")

# ==========================================
# 📤 অ্যাপ শেয়ারিং ইন্টারফেস (Sidebar Share Section)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.title("📤 Share This App")
st.sidebar.write("আপনার বন্ধু বা পরিচিতদের সাথে অ্যাপটি শেয়ার করুন:")

# বর্তমান অ্যাপের ওয়েব লিংক অটো ডিটেক্ট বা শেয়ার টেক্সট তৈরি
app_share_text = "🔥 অসাধারণ একটি ভিডিও শর্ট জেনারেটর অ্যাপ! এই লিংকে ক্লিক করে যেকোনো লং ভিডিও থেকে শর্ট ক্লিপ তৈরি করুন এবং ওয়াটারমার্ক রিমুভ করুন: "
whatsapp_url = f"https://api.whatsapp.com/send?text={app_share_text}"

st.sidebar.markdown(
    f'<a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; width:100%; font-weight:bold;">📲 WhatsApp এ শেয়ার করুন</button></a>',
    unsafe_allow_html=True
)

FREE_LIMIT = 2

# যদি ফ্রি লিমিট শেষ হয়ে যায় এবং ডেভেলপার বা সাবস্ক্রাইব করা না থাকে, তবে সাবস্ক্রিপশন পেজ দেখাবে
if st.session_state.video_count >= FREE_LIMIT and not st.session_state.is_subscribed:
    st.warning("⚠️ আপনার ফ্রি ট্রায়াল লিমিট (২টি ভিডিও) শেষ হয়ে গেছে! অ্যাপটি தொடர்ந்து ব্যবহার করতে একটি প্ল্যান বেছে নিন বা সাইডবার থেকে ডেভেলপার মোড অন করুন।")
    
    st.markdown("---")
    st.subheader("💎 প্রিমিয়াম সাবস্ক্রিপশন প্ল্যানসমূহ")
    st.write("সাধারণ ব্যবহারকারীদের জন্য প্ল্যানসমূহ:")

    plan_choice = st.radio(
        "সাবস্ক্রিপশন প্ল্যান বেছে নিন:",
        (
            "ডেইলি পাস (Daily Pass) - ₹১৯ / দিন",
            "মাসিক প্রো (Monthly Pro) - ₹২৯৯ / মাস",
            "বার্ষিক মেগা (Yearly Mega) - ₹১,৯৯৯ / বছর"
        )
    )

    st.markdown("---")
    st.write("### 💳 পেমেন্ট অপশন (UPI / PayTM / BharatPe / Razorpay)")
    payment_method = st.selectbox(
        "পেমেন্ট মাধ্যম বেছে নিন:",
        ["UPI (Google Pay / PhonePe / Paytm)", "Paytm Wallet", "BharatPe QR / Net Banking", "Credit / Debit Card (Razorpay)"]
    )

    if st.button("পেমেন্ট সম্পন্ন করুন ও সাবস্ক্রাইব করুন"):
        st.session_state.is_subscribed = True
        st.success(f"ধন্যবাদ! আপনি সফলভাবে '{plan_choice}' সাবস্ক্রাইব করেছেন।")
        st.rerun()
        
    st.stop()

# ভিডিও লিংক ইনপুট নেওয়ার অপশন
video_url = st.text_input("ভিডিওর লিংক দিন (যেমন: YouTube Link):", placeholder="https://www.youtube.com/watch?v=...")

if st.button("ভিডিও জেনারেট ও প্রসেস করুন"):
    if video_url:
        try:
            st.info("লিংক থেকে ভিডিও ডাউনলোড এবং প্রসেসিং শুরু হয়েছে...")
            
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': 'downloaded_video.mp4',
                'merge_output_format': 'mp4',
            }
            
            video_title = "Awesome YouTube Short"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_title = info_dict.get('title', 'YouTube Short')
                
            st.success("ভিডিও সফলভাবে ডাউনলোড হয়েছে!")
            
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
            st.success("ওয়াটারমার্ক রিমুভ করে শর্ট ভিডিও তৈরি সফল!")
            
            st.subheader("🤖 অটো জেনারেটেড মেটাডেটা (টাইটেল ও ডেসক্রিপশন)")
            gen_title = f"🔥 {video_title[:50]}... #Shorts #Viral"
            gen_description = f"Watch this amazing moment from the video! Don't forget to like, share and subscribe for more shorts.\n\nOriginal Source: {video_url}\n\n#Shorts #Trending #YouTubeShorts #ViralVideo"
            
            st.markdown(f"**📌 টাইটেল:**")
            st.code(gen_title, language="text")
            
            st.markdown(f"**📝 ডেসক্রিপশন:**")
            st.code(gen_description, language="text")
            
            if not dev_mode:
                st.session_state.video_count += 1
            
        except Exception as e:
            st.error(f"একটি ত্রুটি ঘটেছে: {e}")
    else:
        st.error("দয়া করে একটি সঠিক ভিডিওর লিংক দিন!")

