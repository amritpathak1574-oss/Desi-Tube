import streamlit as st
import os
import json

# Page Config
st.set_page_config(page_title="DesiTube Enterprise", page_icon="📺", layout="wide")
st.title("📺 DesiTube — Advanced Edition")

# ---------------- DATABASE FILES SETUP ----------------
VIDEOS_FILE = "permanent_videos.json"
USERS_FILE = "permanent_users.json"

def load_data(file_name, default_value):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return default_value

def save_data(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

# Default Mock Data (Isme humne 'is_short' ka filter lagaya hai)
default_users = {"amrit": {"password": "123", "channel": "Amrit Coder 🇮🇳", "history": []}}
default_videos = [
    {"id": 1, "title": "Python Premium Game Tutorial", "channel": "Amrit Coder 🇮🇳", "category": "Tech", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "views": 100, "likes": 25, "is_short": False},
    {"id": 2, "title": "When code works on first try! 😂", "channel": "Amrit Coder 🇮🇳", "category": "Comedy", "url": "https://www.w3schools.com/html/movie.mp4", "views": 500, "likes": 120, "is_short": True},
    {"id": 3, "title": "Unboxing New Gaming Laptop", "channel": "TechGuy", "category": "Tech", "url": "https://www.w3schools.com/html/mov_bbb.mp4", "views": 80, "likes": 15, "is_short": False},
    {"id": 4, "title": "Insane Minecraft Clutch!", "channel": "GamerX", "category": "Gaming", "url": "https://www.w3schools.com/html/movie.mp4", "views": 300, "likes": 95, "is_short": True}
]

if "users_db" not in st.session_state:
    st.session_state.users_db = load_data(USERS_FILE, default_users)

if "videos_db" not in st.session_state:
    st.session_state.videos_db = load_data(VIDEOS_FILE, default_videos)

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Selected Channel track karne ke liye (View Channel Feature)
if "selected_channel" not in st.session_state:
    st.session_state.selected_channel = None

# ----------------- SIDEBAR LOGIN -----------------
st.sidebar.title("🔐 Account")
if st.session_state.current_user is None:
    auth_mode = st.sidebar.selectbox("Login / Sign Up", ["Login", "Create Channel"])
    if auth_mode == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Log In"):
            if username in st.session_state.users_db and st.session_state.users_db[username]["password"] == password:
                st.session_state.current_user = username
                st.rerun()
    elif auth_mode == "Create Channel":
        new_user = st.sidebar.text_input("Username")
        new_pass = st.sidebar.text_input("Password", type="password")
        new_channel = st.sidebar.text_input("Channel Name")
        if st.sidebar.button("Register"):
            if new_user and new_pass and new_channel and new_user not in st.session_state.users_db:
                st.session_state.users_db[new_user] = {"password": new_pass, "channel": new_channel, "history": []}
                save_data(USERS_FILE, st.session_state.users_db)
                st.session_state.current_user = new_user
                st.rerun()
else:
    st.sidebar.success(f"Logged in: {st.session_state.current_user}")
    st.sidebar.info(f"📺 Channel: {st.session_state.users_db[st.session_state.current_user]['channel']}")
    if st.sidebar.button("Logout"):
        st.session_state.current_user = None
        st.rerun()

# ----------------- NAVIGATION -----------------
menu = ["🏠 Home Feed", "🩳 Desi Shorts", "🔍 Search Center", "📤 Upload Content"]
# Agar kisi channel par click hua hai, toh menu mein ek extra tab dikhega
if st.session_state.selected_channel:
    menu.append(f"👤 Channel: {st.session_state.selected_channel}")

choice = st.radio("Menu", menu, horizontal=True)

# Helper function to render a video block
def render_video_block(vid, idx):
    st.markdown(f"### {vid['title']}")
    # VIEW CHANNEL FEATURE: Channel ka naam ek button ki tarah dikhega, click karte hi channel page khulega
    if st.button(f"👤 {vid['channel']}", key=f"ch_btn_{vid['id']}_{idx}"):
        st.session_state.selected_channel = vid["channel"]
        st.rerun()
        
    st.caption(f"Category: `{vid['category']}` | 👁️ {vid['views']} views | 👍 {vid['likes']} likes")
    st.video(vid["url"])
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"▶️ Watch (Add View)", key=f"watch_{vid['id']}_{idx}"):
            vid["views"] += 1
            if st.session_state.current_user:
                st.session_state.users_db[st.session_state.current_user]["history"].append(vid["category"])
                save_data(USERS_FILE, st.session_state.users_db)
            save_data(VIDEOS_FILE, st.session_state.videos_db)
            st.rerun()
    with c2:
        # LIKES SYSTEM FEATURE: Real-time likes save honge database mein
        if st.button(f"👍 Like", key=f"like_{vid['id']}_{idx}"):
            vid["likes"] += 1
            save_data(VIDEOS_FILE, st.session_state.videos_db)
            st.toast("Video Liked!")
            st.rerun()
    st.markdown("---")

# ----------------- 1. HOME FEED -----------------
if choice == "🏠 Home Feed":
    st.subheader("🔥 Recommended Videos")
    # Sirf Long videos filter karna (Shorts nahi)
    long_videos = [v for v in st.session_state.videos_db if not v.get("is_short", False)]
    
    if st.session_state.current_user and st.session_state.users_db[st.session_state.current_user]["history"]:
        user_history = st.session_state.users_db[st.session_state.current_user]["history"]
        long_videos.sort(key=lambda x: user_history.count(x["category"]), reverse=True)
        
    cols = st.columns(2)
    for idx, vid in enumerate(long_videos):
        with cols[idx % 2]:
            render_video_block(vid, idx)

# ----------------- 2. SHORTS FEED -----------------
elif choice == "🩳 Desi Shorts":
    st.subheader("📱 Desi Shorts (Scroll & Enjoy)")
    # Sirf Shorts format waali videos filter karna
    shorts_videos = [v for v in st.session_state.videos_db if v.get("is_short", False)]
    
    # Grid thoda patla aur lamba (9:16 vertical feel ke liye)
    cols = st.columns(3)
    for idx, vid in enumerate(shorts_videos):
        with cols[idx % 3]:
            st.markdown(f"#### ⚡ {vid['title']}")
            if st.button(f"👤 {vid['channel']}", key=f"short_ch_{vid['id']}"):
                st.session_state.selected_channel = vid["channel"]
                st.rerun()
            st.video(vid["url"])
            st.write(f"👍 {vid['likes']} | 👁️ {vid['views']}")
            if st.button(f"❤️ Like Short", key=f"short_like_{vid['id']}"):
                vid["likes"] += 1
                save_data(VIDEOS_FILE, st.session_state.videos_db)
                st.rerun()

# ----------------- 3. SEARCH CENTER -----------------
elif choice == "🔍 Search Center":
    st.subheader("🔍 Search Videos and Channels")
    search_query = st.text_input("Kya dekhna chahte ho? (Type title, channel, or category)").lower()
    
    if search_query:
        # Search Matching Logic
        results = [v for v in st.session_state.videos_db if 
                   search_query in v["title"].lower() or 
                   search_query in v["channel"].lower() or 
                   search_query in v["category"].lower()]
        
        if results:
            st.success(f"Humare Algorithm ko {len(results)} videos mili aapke liye:")
            cols = st.columns(2)
            for idx, vid in enumerate(results):
                with cols[idx % 2]:
                    render_video_block(vid, idx)
        else:
            st.error("Oops! Aisa koi video ya channel nahi mila.")

# ----------------- 4. VIEW CHANNEL PAGE -----------------
elif choice.startswith("👤 Channel:"):
    st.header(f"📺 Channel Page: {st.session_state.selected_channel}")
    
    # Us channel ki saari videos filter karna
    channel_vids = [v for v in st.session_state.videos_db if v["channel"] == st.session_state.selected_channel]
    
    # Calculate Stats
    total_views = sum(v["views"] for v in channel_vids)
    total_likes = sum(v["likes"] for v in channel_vids)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🎬 Total Videos", len(channel_vids))
    c2.metric("👁️ Total Lifetime Views", total_views)
    c3.metric("❤️ Total Likes", total_likes)
    
    st.write("### Uploaded Content:")
    cols = st.columns(2)
    for idx, vid in enumerate(channel_vids):
        with cols[idx % 2]:
            st.markdown(f"#### {vid['title']} {'(🩳 Short)' if vid.get('is_short') else ''}")
            st.video(vid["url"])
            st.write(f"👁️ {vid['views']} views | 👍 {vid['likes']} likes")
    
    if st.button("⬅️ Back to Home"):
        st.session_state.selected_channel = None
        st.rerun()

# ----------------- 5. UPLOAD CONTENT -----------------
elif choice == "📤 Upload Content":
    st.header("📤 Creator Studio")
    if st.session_state.current_user is None:
        st.warning("Pehle login karo tabhi upload kar paoge!")
    else:
        user_channel = st.session_state.users_db[st.session_state.current_user]["channel"]
        with st.form("upload_form"):
            title = st.text_input("Video/Short Title")
            category = st.selectbox("Category", ["Tech", "Gaming", "Music", "Comedy", "Vlogs"])
            video_url = st.text_input("Video MP4 URL")
            # SHORTS SELECTION OPTION
            is_short = st.checkbox("Kya ye ek 15-second Short Video hai?")
            
            submit = st.form_submit_button("Publish Content")
            if submit and title and video_url:
                new_vid = {
                    "id": len(st.session_state.videos_db) + 1,
                    "title": title,
                    "channel": user_channel,
                    "category": category,
                    "url": video_url,
                    "views": 0,
                    "likes": 0,
                    "is_short": is_short # True agar tick kiya hai
                }
                st.session_state.videos_db.append(new_vid)
                save_data(VIDEOS_FILE, st.session_state.videos_db)
                st.success(f"🎉 Published successfully as {'Short' if is_short else 'Video'}!")
