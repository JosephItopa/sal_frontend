import streamlit as st
import requests
from datetime import date


# App Config

st.set_page_config(
    page_title="Media Search App",
    layout="wide"
)

### import requests

def download_audio_file(url: str):
    """
    Fetch audio file bytes for download.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.content


# Session State

if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "last_response" not in st.session_state:
    st.session_state.last_response = {"videos": [], "audios": []}


# Mock API Call (Replace)

# Mock API Call (Replace)
def fetch_results(payload: dict):
    """
    Replace this with your real API call.
    """
    if payload["mode"] == "Manual Search":
        response = requests.post("https://sal-ai-agent-pipeline.onrender.com/search/manual", json=payload)
    else:
        response = requests.post("https://sal-ai-agent-pipeline.onrender.com/search/prompt", json=payload)

    return response.json()


@st.cache_data(show_spinner=False)
def fetch_audio_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content

def fetch_audio_with_progress(url: str) -> bytes:
    progress_bar = st.progress(0)
    status = st.empty()

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0
    chunks = []

    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)

            if total:
                progress_bar.progress(min(downloaded / total, 1.0))
                status.text(f"Downloading... {downloaded // 1024} KB")

    progress_bar.empty()
    status.empty()

    return b"".join(chunks)



def render_waveform(audio_bytes: bytes):
    y, sr = librosa.load(BytesIO(audio_bytes), sr=None, mono=True, duration=60)

    fig, ax = plt.subplots(figsize=(8, 2))
    ax.plot(y, linewidth=0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Waveform", fontsize=10)

    st.pyplot(fig, clear_figure=True)


# LEFT SIDEBAR – INPUTS

with st.sidebar:
    st.header(" Search Parameters")

    mode = st.selectbox(
        "Search Mode",
        ["Manual Search", "AI Chat Search"]
    )

    payload = {"mode": mode}

    if mode == "Manual Search":
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        keywords = st.text_input("Keywords")
        preacher = st.text_input("Preacher Name")

        payload.update({
            "start_date": str(start_date),
            "end_date": str(end_date),
            "keywords": keywords,
            "preacher": preacher
        })

    else:
        prompt = st.text_area(
            "AI Prompt",
            placeholder="e.g. Find sermons about faith by Apostle Michael Orokpo"
        )
        payload.update({"prompt": prompt})

    search_btn = st.button("Search")


# RIGHT SIDEBAR – HISTORY

with st.sidebar:
    st.markdown("---")
    st.header(" Search History")

    if st.session_state.search_history:
        for idx, item in enumerate(reversed(st.session_state.search_history), 1):
            st.markdown(f"**{idx}. {item['mode']}**")
            st.caption(item.get("summary", ""))
    else:
        st.caption("No searches yet")


# MAIN CONTENT

if search_btn:
    response = fetch_results(payload)

    st.session_state.last_response = response
    st.session_state.search_history.append({
        "mode": mode,
        "summary": payload.get("keywords") or payload.get("prompt", "")
    })

videos = st.session_state.last_response.get("videos", [])
audios = st.session_state.last_response.get("audios", [])


# VIDEO SECTION

st.subheader(" Video Results")

if videos:
    for video in videos:
        with st.expander(video["title"]):
            st.video(video["url"])
else:
    st.info("No video results found")

st.divider()

# AUDIO SECTION

st.subheader(" Audio Results")

if audios:
    for idx, audio in enumerate(audios):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**{audio['title']}**")

        with col2:
            try:
                audio_bytes = download_audio_file(audio["url"])
                st.download_button(
                    label="Download",
                    data=audio_bytes,
                    file_name=f"{audio['title'].replace(' ', '_')}.mp3",
                    mime="audio/mpeg",
                    key=f"audio_download_{idx}"
                )
            except Exception as e:
                st.error("Download unavailable")
else:
    st.info("No audio results found")

