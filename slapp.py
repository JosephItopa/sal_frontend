import streamlit as st


# Page Config

st.set_page_config(
    page_title="Message Recommendation App",
    layout="wide",
    # page_icon=""
)


# Mock API function
# Replace this with your real backend API call

def mock_api_search(query: str):
    return {
        "videos": [
            {"title": "The Ministry of Light", "url": "https://www.youtube.com/watch?v=xxxx"},
            {"title": "Salvation Message", "url": "https://www.youtube.com/watch?v=yyyy"},
        ],
        "audios": [
            {"title": "Audio Teaching 1", "url": "https://example.com/audio1.mp3"},
            {"title": "Audio Teaching 2", "url": "https://example.com/audio2.mp3"},
        ]
    }


# Sidebar – Query Results

with st.sidebar:
    st.header("🔍 Current Search Results")
    st.markdown("Videos and audios will appear here after search")

    if "result" in st.session_state:
        videos = st.session_state["result"].get("videos", [])
        audios = st.session_state["result"].get("audios", [])

        st.subheader("🎥 Videos")
        for vid in videos:
            st.markdown(f"- [{vid['title']}]({vid['url']})")

        st.subheader("🎧 Audios")
        for aud in audios:
            st.markdown(f"- [{aud['title']}]({aud['url']})")


# Main Body Layout

st.title("🎬 Message Recommendation App")


# SECTION 1: Input Area

st.subheader("Tell us about your mood")
query = st.text_area("Type your request:", height=120)

if st.button("recommend"):
    if query.strip():
        st.session_state["result"] = mock_api_search(query)
        st.success("Search completed!")

# Fetch saved results
results = st.session_state.get("result", {"videos": [], "audios": []})


# SECTION 2: Recommended Videos

st.subheader(" Recommended Videos")

video_results = results.get("videos", [])
selected_video = None

if video_results:
    titles = [v["title"] for v in video_results]
    selected_title = st.selectbox("Choose a video to watch:", ["Select..."] + titles)

    if selected_title != "Select...":
        selected_video = next(v for v in video_results if v["title"] == selected_title)
        youtube_url = selected_video["url"]

        # Extract ID for YouTube embed
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            st.video(embed_url)
else:
    st.info("No videos found. Search to populate results.")


# SECTION 3: Recommended Audios

st.subheader("Recommended Audios")

audio_results = results.get("audios", [])

if audio_results:
    for audio in audio_results:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(audio["title"])
        with col2:
            st.download_button(
                label="Download",
                data=f"Downloaded from: {audio['url']}",
                file_name=audio["title"].replace(" ", "_") + ".txt"
            )
else:
    st.info("No audios found. Search to populate results.")