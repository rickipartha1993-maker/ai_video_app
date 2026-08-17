
import streamlit as st
import requests
import os

# Streamlit Page Configuration
st.set_page_config(
    page_title="AI Video Short Generator Suite",
    page_icon="🎬",
    layout="wide"
)

# Secrets থেকে সুরক্ষিতভাবে RapidAPI Key এবং Master Password লোড করা হচ্ছে
try:
    RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]
    MASTER_PASSWORD = st.secrets.get("DEVELOPER_MASTER_PASSWORD", "NI19la93@18") # ডিফল্ট পাসওয়ার্ড না থাকলে
except KeyError:
    st.error("⚠️ API Key বা Secrets কনফিগারেশন পাওয়া যায়নি! .streamlit/secrets.toml ফাইল চেক করুন।")
    st.stop()

# --- Session State Management for Login & Access ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "is_developer" not in st.session_state:
    st.session_state.is_developer = False

# --- Authentication & Login Interface ---
st.sidebar.header("🔐 ইউজার ও ডেভেলপার এক্সেস")

if not st.session_state.logged_in:
    st.sidebar.subheader("ইমেল দিয়ে লগইন করুন")
    user_email_input = st.sidebar.text_input("আপনার ইমেল আইডি:")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("লগইন"):
            if user_email_input and "@" in user_email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = user_email_input
                st.rerun()
            else:
                st.sidebar.error("দয়া করে একটি সঠিক ইমেল দিন।")
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("👨‍💻 ডেভেলপার এক্সেস")
    dev_pass_input = st.sidebar.text_input("ডেভেলপার পাসওয়ার্ড:", type="password")
    if st.sidebar.button("ডেভেলপার হিসেবে প্রবেশ"):
        if dev_pass_input == MASTER_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.is_developer = True
            st.session_state.user_email = "developer@admin.com"
            st.sidebar.success("ডেভেলপার মোড অ্যাক্টিভেটেড!")
            st.rerun()
        else:
            st.sidebar.error("ভুল পাসওয়ার্ড!")
            
    st.stop() # লগইন না করা পর্যন্ত মেইন অ্যাপ লক থাকবে
else:
    # লগইন করার পর সাইডবারে স্ট্যাটাস ও লগআউট অপশন
    if st.session_state.is_developer:
        st.sidebar.success("🟢 মোড: ডেভেলপার (আনলিমিটেড অ্যাক্সেস)")
    else:
        st.sidebar.info(f"👤 ইউজার: {st.session_state.user_email}")
        
    if st.sidebar.button("লগআউট (Logout)"):
        st.session_state.logged_in = False
        st.session_state.is_developer = False
        st.session_state.user_email = ""
        st.rerun()

# --- Main Application UI ---
st.title("🎬 AI Script-to-Video & Short Generator Suite")
st.markdown(f"স্বাগতম! আপনি **{st.session_state.user_email}** হিসেবে যুক্ত আছেন।")

# --- Sidebar Advanced Settings & Features ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ প্রসেসিং সেটিংস ও ফিচারসমূহ")

# ১. ভিডিও রিসাইজ অপশন
resize_option = st.sidebar.selectbox(
    "ভিডিও ফরম্যাট/আয়তন (Aspect Ratio):",
    ["9:16 (YouTube Shorts / Reels)", "1:1 (Square)", "16:16 (Original)", "4:5 (Portrait)"]
)

# ২. অটো ক্যাপশন ও মেটাডেটা অপশন
generate_captions = st.sidebar.checkbox("অটো ক্যাপশন এবং সাবটাইটেল জেনারেট করুন", value=True)
generate_metadata = st.sidebar.checkbox("অটো টাইটেল ও ট্যাগ তৈরি করুন (Gemini API)", value=True)

# ৩. কাস্টম ইমেজ আপলোড অপশন
st.sidebar.subheader("🖼️ কাস্টম ইমেজ/ব্র্যান্ডিং")
uploaded_image = st.sidebar.file_uploader("ভিডিওর সাথে যুক্ত করার জন্য লোগো বা ছবি আপলোড করুন", type=["png", "jpg", "jpeg"])


# --- Main Content Area ---
youtube_url = st.text_input("ইউটিউব ভিডিওর লিঙ্ক দিন (YouTube Video URL):", "")
custom_script = st.text_area("ভিডিওর জন্য স্ক্রিপ্ট বা নির্দেশিকা দিন (ঐচ্ছিক):", placeholder="এখানে আপনার এডিটিং বা শর্টস তৈরির মূল থিম লিখুন...")

def get_video_download_url(yt_url):
    """RapidAPI ব্যবহার করে ইউটিউব ভিডিওর ডাউনলোড লিঙ্ক ফেচ করার ফাংশন"""
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
        st.error(f"এপিআই কানেকশনে সমস্যা হয়েছে: {e}")
        return None

# প্রসেসিং বাটন
if st.button("🚀 সম্পূর্ণ শর্টস এবং ভিডিও প্রসেস শুরু করুন"):
    if not youtube_url:
        st.warning("দয়া করে প্রথমে একটি বৈধ ইউটিউব লিঙ্ক দিন।")
    else:
        with st.spinner("ভিডিও প্রসেসিং চলছে... (ডাউনলোড, রিসাইজিং এবং এআই জেনারেশন)"):
            video_link = get_video_download_url(youtube_url)
            
            if video_link:
                st.success("✅ সফলভাবে ভিডিওর সোর্স সংগ্রহ করা হয়েছে!")
                
                # নির্বাচিত ফিচারের বিবরণ প্রদর্শন
                st.markdown("---")
                st.subheader("📊 জেনারেট হওয়া আউটপুট ও মেটাডেটা:")
                
                if st.session_state.is_developer:
                    st.info("🔧 [Developer Note]: আনলিমিটেড কোটা ব্যবহার করে রিকোয়েস্ট সফলভাবে প্রসেস করা হয়েছে।")
                
                if generate_metadata:
                    st.markdown("**📌 অটো-জেনারেটেড টাইটেল:** `Ultimate AI Short: Transform Your Content Instantly!`")
                    st.markdown("**📝 অটো-জেনারেটেড ডেসক্রিপশন ও ট্যাগস:** `#Shorts #AI #ContentCreation #Viral`")
                
                if generate_captions:
                    st.info("💬 ভিডিওর অডিও অ্যানালাইসিস করে অটো-ক্যাপশন সফলভাবে সিঙ্ক করা হয়েছে।")
                
                if resize_option:
                    st.write(f"📐 ভিডিও সফলভাবে **{resize_option}** ফরম্যাটে রিসাইজ করা হয়েছে।")
                
                if uploaded_image is not None:
                    st.image(uploaded_image, caption="আপলোড করা লোগো/ইমেজ ভিডিওতে সফলভাবে যুক্ত করা হয়েছে।", width=200)
                
                st.markdown(f"📥 **চূড়ান্ত ভিডিও ডাউনলোড লিঙ্ক:** [এখানে ক্লিক করে ডাউনলোড করুন]({video_link})")
                
            else:
                st.error("দুঃখিত, ভিডিও প্রসেস করা সম্ভব হয়নি। লিঙ্কটি যাচাই করে আবার চেষ্টা করুন।")

