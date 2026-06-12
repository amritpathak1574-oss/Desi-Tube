import streamlit as st
import os
import json

# Page Config
st.set_page_config(page_title="DesiTube Permanent", page_icon="📺", layout="wide")
st.title("📺 DesiTube — Fixed & Permanent Edition")

# ---------------- DATABASE FILES SETUP ----------------
# Do files banayenge permanent storage ke liye
VIDEOS_FILE = "permanent_videos.json"
USERS_FILE = "permanent_users.json"

# Helper Function: Data load karne ke liye
def load_data(file_name, default_value):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return default_value

# Helper Function: Data save karne ke liye
def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

# Shuruati data agar files khali hain
default_users = {"amrit": {"password": "123", "channel": "Amrit Coder 🇮🇳", "history": []}}
default_videos = [
    {"id": 1, "title": "Python Premium Game Tutorial", "channel": "Amrit Coder 🇮🇳", "category": "Tech", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "views": 100, "likes": 25}
]

# JSON se data load karke Session State mein daalna (Sirf ek baar)
if "users_db" not in st.session_state:
    st.session_state.users_db = load_data(USERS_FILE, default_users)

if "videos_db" not in st.session_state:
    st.session_state.videos_db = load_data(VIDEOS_FILE, default_videos)

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ----------------- SIDEBAR AUTHENTICATION -----------------
st.sidebar.title("🔐 User Account")

if st.session_state.current_user is None:
    auth_mode = st.sidebar.selectbox("Login / Sign Up", ["Login", "Create Channel"])
    
    if auth_mode == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In"):
            if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                st.session_state.current_user = username
                st.sidebar.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Galat password ya username!")
                
    elif auth_mode == "Create Channel":
        new_user = st.sidebar.text_input("Choose Username")
        new_pass = st.sidebar.text_input("Choose Password", type="password")
        new_channel = st.sidebar.text_input("Channel Name")
        
        if st.sidebar.button("Register Channel"):
            if new_user and new_pass and new_channel:
                if new_user not in st.session_state.users_db:
                    # Session state update karo
                    st.session_state.users_db[new_user] = {
                        "password": new_pass,
                        "channel": new_channel,
                        "history": []
                    }
                    # PERMANENT SAVE: File mein write karo
                    save_data(USERS_FILE, st.session_state.users_db)
                    
                    st.session_state.current_user = new_user
                    st.sidebar.success("Channel Saved Permanently! 🎉")
                    st.rerun()
                else:
                    st.sidebar.error("Username already exists!")
else:
    user_info = st.session_state.users_db[st.session_state.current_user]
    st.sidebar.success(f"Logged in: **{st.session_state.current_user}**")
    st.sidebar.info(f"📺 Channel: **{user_info['channel']}**")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

# ----------------- MAIN APP -----------------
menu = ["🏠 Home (Smart Feed)", "📤 Upload Content"]
choice = st.radio("Menu", menu, horizontal=True)

# ALGORITHM: Sorting based on history
if choice == "🏠 Home (Smart Feed)":
    all_videos = st.session_state.videos_db.copy()
    
    # Check history for algorithm
    if st.session_state.current_user and st.session_state.users_db[st.session_state.current_user]["history"]:
        user_history = st.session_state.users_db[st.session_state.current_user]["history"]
        all_videos.sort(key=lambda x: user_history.count(x["category"]), reverse=True)
        st.write("✨ **Recommended For You**")
    else:
        all_videos.sort(key=lambda x: x["views"], reverse=True)
        st.write("🔥 **Trending Feed**")
        
    cols = st.columns(2)
    for idx, vid in enumerate(all_videos):
        with cols[idx % 2]:
            st.markdown(f"### {vid['title']}")
            st.caption(f"Channel: {vid['channel']} | Category: `{vid['category']}`")
            st.video(vid["url"])
            
            if st.button(f"▶️ Watch Video", key=f"watch_{vid['id']}"):
                # View count badhao session state mein
                vid["views"] += 1
                
                # History add karo
                if st.session_state.current_user:
                    st.session_state.users_db[st.session_state.current_user]["history"].append(vid["category"])
                    save_data(USERS_FILE, st.session_state.users_db) # Save user history
                
                # PERMANENT SAVE: Video views database file mein save karo
                save_data(VIDEOS_FILE, st.session_state.videos_db)
                st.rerun()
                
            st.write(f"👁️ {vid['views']} views | 👍 {vid['likes']} likes")
            st.markdown("---")

# ----------------- UPLOAD PAGE -----------------
elif choice == "📤 Upload Content":
    st.header("📤 Creator Studio")
    
    if st.session_state.current_user is None:
        st.warning("Bhai, pehle side panel se login karo!")
    else:
        user_channel = st.session_state.users_db[st.session_state.current_user]["channel"]
        
        with st.form("upload_form"):
            title = st.text_input("Video Title")
            category = st.selectbox("Category", ["Tech", "Gaming", "Music", "Vlogs"])
            video_url = st.text_input("Video MP4 URL")
            
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
                # Session State mein daalo
                st.session_state.videos_db.append(new_vid)
                
                # PERMANENT SAVE: File mein video save karo
                save_data(VIDEOS_FILE, st.session_state.videos_db)
                
                st.success(f"🎉 '{title}' ab permanently save ho gayi hai!")
