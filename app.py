import requests
import streamlit as st
from datetime import date

# App Config
st.set_page_config(
    page_title="Spirit-and-Life",
    layout="wide"
)


# Session State
if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "last_response" not in st.session_state:
    st.session_state.last_response = {"videos": [], "audios": []}


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


# LEFT SIDEBAR – INPUTS
with st.sidebar:
    st.header(" Search Parameters")

    mode = st.selectbox(
        "Search Mode",
        ["Manual Search", "AI Chat Search"]
    )

    payload = {"mode": mode}

    if mode == "Manual Search":
        #start_date = st.date_input("Start Date") # , value=date.today()
        #end_date = st.date_input("End Date")
        keywords = st.text_input("Keywords")
        preacher = st.text_input("Preacher Name")

        payload.update({
            "start_date": None, #str(start_date),
            "end_date": None, #str(end_date),
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
#st.subheader(" Audio Results")

#if audios:
#    for audio in audios:
#        with st.expander(audio["message_title"]):
#            #st.audio(audio["preacher"])
#            st.audio(audio["url"])
#else:
#    st.info("No audio results found")

st.subheader("Audio Results")

if audios:
    for idx, audio in enumerate(audios):
        title = audio.get("message_title", "Untitled Audio")
        preacher = audio.get("preacher", "")

        expander_title = (
            f"{title} — {preacher}" if preacher else title
        )

        with st.expander(expander_title):
            try:
                audio_bytes = fetch_audio_bytes(audio["url"])

                # Stream audio
                st.audio(audio_bytes, format="audio/mp3")

                # Download audio
                st.download_button(
                    label="Download",
                    data=audio_bytes,
                    file_name=f"{title.replace(' ', '_')}.mp3",
                    mime="audio/mpeg",
                    key=f"audio_dl_{idx}"
                )

            except Exception:
                st.error("Audio unavailable")
else:
    st.info("No audio results found")
