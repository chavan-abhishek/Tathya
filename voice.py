import streamlit as st
from streamlit_mic_recorder import speech_to_text


def record_voice(language="en"):
    state = st.session_state
    if "text_received" not in state:
        state.text_received = []
    text = speech_to_text(
        start_prompt="🎙️",
        stop_prompt="⚠️Stop",
        language=language,
        use_container_width=True,
        just_once=True,
    )
    if text:
        state.text_received.append(text)
    result = ""
    for text in state.text_received:
        result += text

    state.text_received = []
    return result if result else None
