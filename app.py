import streamlit as st
import os

# 1. Page Configuration
st.set_page_config(page_title="DesiTube Enterprise", page_icon="📺", layout="wide")

# Database Initialization in Session State
if "users_db" not in st.session_state:
    # Users database format: {username: {password: pass, channel: channel_name, history: [tags]}}
    st.session_state.users_db = {
        "amrit": {"password": "123", "channel": "Amrit Coder 🇮🇳", "history": ["Tech", "Gaming"]}
    }

if "videos_db" not in st.session_state:
    # Videos ke saath hum 'category' ya 'tags' add kar rahe hain algorithm ke liye
    st.session_state.videos_db = [
        {"id": 1, "title": "Python Game Development Tutorial", "channel": "Amrit Coder 🇮🇳", "category": "Tech", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "views": 150, "likes": 40},
        {"id": 2, "title": "Minecraft Speedrun World Record", "channel": "GamerX", "category": "Gaming", "url": "https://www.w3schools.com/html/movie.mp4", "views": 90, "likes": 30},
        {"id": 3, "title": "Top 10 Lo-Fi Beats to Study", "channel": "ChillVibes", "category": "Music", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "views": 200, "likes": 85},
        {"id": 4, "title": "Building a Tech Startup in India", "channel": "Amrit Coder 🇮🇳", "category": "Tech", "url": "https://www.w3schools.com/html/movie.mp4", "views": 310, "likes": 120}
    ]

if "current_user" not in st.session_state:
    st.session_state.current_user = None # Shuru mein koi login nahi hai

# ----------------- SIDEBAR AUTHENTICATION SYSTEM -----------------
st.sidebar.title("🔐 User Account")

if st.session_state.current_user is None:
    auth_mode = st.sidebar.selectbox("Login ya Sign Up karo", ["Login", "Create Channel (Sign Up)"])
    
    if auth_mode == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In"):
            if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                st.session_state.current_user = username
                st.sidebar.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Wrong Username or Password!")
                
    elif auth_mode == "Create Channel (Sign Up)":
        new_user = st.sidebar.text_input("Choose Username")
        new_pass = st.sidebar.text_input("Choose Password", type="password")
        new_channel = st.sidebar.text_input("Your Channel Name (e.g., T-Series Mini)")
        
        if st.sidebar.button("Register & Create Channel"):
            if new_user and new_pass and new_channel:
                if new_user not in st.session_state.users_db:
                    st.session_state.users_db[new_user] = {
                        "password": new_pass,
                        "channel": new_channel,
                        "history": [] # Naye user ki history shuru mein khali hogi
                    }
                    st.session_state.current_user = new_user
                    st.sidebar.success("Channel Created Successfully! 🎉")
                    st.rerun()
                else:
                    st.sidebar.error("Username pehle se hi le rakha hai kisi ne!")
else:
    user_info = st.session_state.users_db[st.session_state.current_user]
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    st.sidebar.info(f"📺 Channel: **{user_info['channel']}**")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

# ----------------- MAIN APP NAVIGATION -----------------
menu = ["🏠 Home (Smart Feed)", "📤 Upload Content"]
choice = st.radio("Menu", menu, horizontal=True)

# ALGORITHM LOGIC: Smart Feed Content Recommender
def get_recommended_videos():
    all_videos = st.session_state.videos_db.copy()
    
    # Agar user logged in hai aur uski koi watch history hai
    if st.session_state.current_user and st.session_state.users_db[st.session_state.current_user]["history"]:
        user_history = st.session_state.users_db[st.session_state.current_user]["history"]
        
        # Ek key banate hain algorithm ke liye jo preferred category ko upar rakhegi
        # Jo category history mein sabse zyada hogi, uski videos pehle aayengi
        def algo_sort_key(video):
            # Jitni baar category history mein aayi hai, utni priority badhao
            priority = user_history.count(video["category"])
            return priority
        
        # Videos ko custom weight ke hisab se sort karna (Highest priority first)
        all_videos.sort(key=algo_sort_key, reverse=True)
        return all_videos, True
    else:
        # Agar user login nahi hai to views ke hisab se "Trending Videos" dikhao
        all_videos.sort(key=lambda x: x["views"], reverse=True)
        return all_videos, False

# ----------------- PAGE 1: HOME (SMART FEED) -----------------
if choice == "🏠 Home (Smart Feed)":
    videos, is_personalized = get_recommended_videos()
    
    if is_personalized:
        st.write("✨ **Recommended For You** (Based on your interest/history)")
    else:
        st.write("🔥 **Trending Feed** (Log in to get personalized recommendations!)")
        
    # Grid Layout to show videos
    cols = st.columns(2)
    for idx, vid in enumerate(videos):
        with cols[idx % 2]:
            st.markdown(f"### {vid['title']}")
            st.caption(f"📺 Channel: {vid['channel']} | 🏷️ Category: `{vid['category']}`")
            st.video(vid["url"])
            
            # Watch Video button jo history aur views track karega
            if st.button(f"▶️ Watch & Interact", key=f"watch_{vid['id']}"):
                # 1. View Count Badhana
                vid["views"] += 1
                
                # 2. Algorithm Trigger: History register karna (sirf agar logged in ho)
                if st.session_state.current_user:
                    st.session_state.users_db[st.session_state.current_user]["history"].append(vid["category"])
                    st.toast(f"Algorithm Updated: Prefers {vid['category']}! 🚀")
                st.rerun()
                
            st.write(f"👁️ {vid['views']} views | 👍 {vid['likes']} likes")
            st.markdown("---")

# ----------------- PAGE 2: UPLOAD CONTENT -----------------
elif choice == "📤 Upload Content":
    st.header("📤 Creator Dashboard")
    
    if st.session_state.current_user is None:
        st.warning("Bhai, pehle side panel se login karo ya apna Channel banao tabhi upload kar paoge!")
    else:
        user_channel = st.session_state.users_db[st.session_state.current_user]["channel"]
        st.write(f"Uploading as: **{user_channel}**")
        
        with st.form("upload_form"):
            title = st.text_input("Video Title")
            category = st.selectbox("Video Category (For Algorithm)", ["Tech", "Gaming", "Music", "Vlogs"])
            video_url = st.text_input("Paste Video MP4 URL (e.g., https://www.w3schools.com/html/mov_bbb.mp4)")
            
            submit = st.form_submit_button("Publish Video")
            if submit and title and video_url:
                new_vid = {
                    "id": len(st.session_state.videos_db) + 1,
                    "title": title,
                    "channel": user_channel,
                    "category": category,
                    "url": video_url,
                    "views": 0,
                    "likes": 0
                }
                st.session_state.videos_db.append(new_vid)
                st.success(f"🎉 Boom! '{title}' is now live under category {category}!")
