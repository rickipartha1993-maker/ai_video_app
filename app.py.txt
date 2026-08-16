
import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import os

st.title("AI Video Short Generator")

api_key = st.text_input("Gemini API Key দাও", type="password")
uploaded_file = st.file_uploader("ভিডিও আপলোড করো", type=["mp4"])

if st.button("ভিডিও জেনারেট করো"):
    if api_key and uploaded_file:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        
        st.write("ভিডিও প্রসেসিং শুরু হয়েছে...")
        # এখানে তোমার ভিডিও কাটার লজিক বা জেমিনি এপিআই কল বসবে
        
        st.success("ভিডিও তৈরি সফল!")
    else:
        st.error("API Key এবং ভিডিও ফাইল দাও!")

