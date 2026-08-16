

import os
import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import yt_dlp

# Page configuration
st.set_page_config(page_title="AI Video Short Generator", page_icon="🎥", layout="centered")

st.title("🎥 AI Video Short & Metadata Generator")
st.write("যে কোনো লং ভিডিওর লিংক দিন, এআই নিজে থেকেই শর্টস এবং আকর্ষণীয় টাইটেল-ডেসক্রিপশন তৈরি করে দেবে!")

# সেশন স্টেট (Session State) ট্র্যাকিং
if 'video_count' not in st.session_state:
    st.session_state.video_count = 0

if 'is_subscribed' not in st.session_state:
    st.session_state.is_subscribed = False

FREE_LIMIT = 2

# যদি ফ্রি লিমিট শেষ হয়ে যায় এবং সাবস্ক্রাইব করা না থাকে, তবে সাবস্ক্রিপশন পেজ দেখাবে
if st.session_state.video_count >= FREE_LIMIT and not st.session_state.is_subscribed:
    st.warning("⚠️ আপনার ফ্রি ট্রায়াল লিমিট (২টি ভিডিও) শেষ হয়ে গেছে! অ্যাপটি தொடர்ந்து ব্যবহার করতে একটি প্ল্যান বেছে নিন।")
    
    st.markdown("---")
    st.subheader("💎 প্রিমিয়াম সাবস্ক্রিপশন প্ল্যানসমূহ")
    st.write("আপনার পছন্দের প্ল্যানটি সিলেক্ট করুন এবং পেমেন্ট সম্পন্ন করুন:")

    # প্রাইসিং প্ল্যান কার্ড বা অপشن
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
    st.info("নিচের যেকোনো পেমেন্ট মেথড ব্যবহার করে পেমেন্ট করতে পারেন:")

    # পেমেন্ট মেথড সিলেক্ট করার অপশন
    payment_method = st.selectbox(
        "পেমেন্ট মাধ্যম বেছে নিন:",
        ["UPI (Google Pay / PhonePe / Paytm)", "Paytm Wallet", "BharatPe QR / Net Banking", "Credit / Debit Card (Razorpay)"]
    )

    # পেমেন্ট কনফার্ম করার বাটন
    if st.button("পেমেন্ট সম্পন্ন করুন ও সাবস্ক্রাইব করুন"):
        # এখানে সফল পেমেন্টের পর সাবস্ক্রিপশন সচল করার লজিক
        st.session_state.is_subscribed = True
        st.success(f"ধন্যবাদ! আপনি সফলভাবে '{plan_choice}' সাবস্ক্রাইব করেছেন ({payment_method} এর মাধ্যমে)।")
        st.rerun()
        
    st.stop() # সাবস্ক্রিপশন না নিলে নিচের অংশ রান করবে না

# ব্যাকগ্রাউন্ডে সিক্রেট থেকে এপিআই কি কনফিগার করা
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    st.error("সার্ভার কনফিগারেশনে জেমিনাই এপিআই কি (GEMINI_API_KEY) পাওয়া যায়নি। দয়া করে Streamlit Secrets-এ কি-টি যুক্ত করুন।")

# ভিডিও লিংক ইনপুট নেওয়ার অপশন
video_url = st.text_input("ভিডিওর লিংক দিন (যেমন: YouTube Link):", placeholder="https://www.youtube.com/watch?v=...")

if st.button("ভিডিও জেনারেট ও প্রসেস করুন"):
    if video_url:
        try:
            st.info("লিংক থেকে ভিডিও ডাউনলোড এবং প্রসেসিং শুরু হয়েছে...")
            
            # yt-dlp দিয়ে লিংক থেকে ভিডিও ডাউনলোড
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                'outtmpl': 'downloaded_video.mp4',
                'merge_output_format': 'mp4',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
            st.success("ভিডিও সফলভাবে ডাউনলোড হয়েছে!")
            
            # MoviePy দিয়ে ভিডিও প্রসেসিং
            video_path = "downloaded_video.mp4"
            clip = VideoFileClip(video_path)
            
            # উদাহরণস্বরূপ প্রথম ৩০ সেকেন্ডের শর্ট ক্লিপ তৈরি
            short_clip = clip.subclip(0, min(30, clip.duration))
            output_path = "output_short.mp4"
            
            short_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                bitrate="5000k",
                preset="medium"
            )
            
            st.video(output_path)
            st.success("ফুল এইচডি শর্ট ভিডিও তৈরি সফল!")
            
            # অটো টাইটেল ও ডেসক্রিপশন জেনারেট
            st.subheader("🤖 এআই জেনারেটেড মেটাডেটা (টাইটেল ও ডেসক্রিপশন)")
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Give an attractive YouTube Shorts title and a short description with relevant hashtags for a video created from this link: " + video_url
                response = model.generate_content(prompt)
                st.write(response.text)
            except Exception as e:
                st.warning(f"মেটাডেটা তৈরি করতে সমস্যা হয়েছে: {e}")
                
            # ভিডিও কাউন্ট ১ বাড়িয়ে দেওয়া
            st.session_state.video_count += 1
            
        except Exception as e:
            st.error(f"একটি ত্রুটি ঘটেছে: {e}")
    else:
        st.error("দয়া করে একটি সঠিক ভিডিওর লিংক দিন!")

