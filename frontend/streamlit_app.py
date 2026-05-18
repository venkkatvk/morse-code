"""Streamlit UI for the Morse Code Interpreter application."""

import json
from pathlib import Path

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"
TEXT_ENDPOINT = f"{BACKEND_URL}/translate-text"
AUDIO_ENDPOINT = f"{BACKEND_URL}/translate-audio"


def render_translation_result(response: dict) -> None:
    """Display a structured Morse translation response in the Streamlit UI."""
    translation = response.get("translation") or response
    if not translation:
        st.error("Received unexpected response format from the backend.")
        return

    status = "Corrupted fallback was used" if translation.get("is_corrupted") else "Translation completed successfully"
    st.markdown(f"**Status:** {status}")
    st.markdown("---")
    st.markdown(f"**Translated Text:** {translation.get('translated_text')}")
    st.markdown(f"**Confidence Score:** {translation.get('confidence_score'):.2f}")
    st.markdown(f"**Corrupted Output:** {translation.get('is_corrupted')}")

    if response.get("sample_rate") is not None:
        st.markdown("---")
        st.markdown(f"**Sample Rate:** {response['sample_rate']} Hz")
        st.markdown(f"**Duration:** {response['duration_seconds']:.2f} seconds")
        st.markdown(f"**RMS:** {response['rms']:.4f}")
        st.markdown(f"**Noise Floor:** {response['noise_floor']:.4f}")


def submit_text_translation(morse_code: str) -> dict:
    """Send a manual Morse code string to the text translation endpoint."""
    payload = {"morse_code": morse_code, "modality": "text"}
    response = requests.post(TEXT_ENDPOINT, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def submit_audio_translation(uploaded_file) -> dict:
    """Send a WAV file upload to the audio translation endpoint."""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "audio/wav")}
    response = requests.post(AUDIO_ENDPOINT, files=files, timeout=60)
    response.raise_for_status()
    return response.json()


def main() -> None:
    """Render the Streamlit interface."""
    st.set_page_config(page_title="Morse Code Interpreter", layout="centered")
    st.title("Morse Code Interpreter")
    st.markdown(
        "Use the text input to paste Morse code directly, or upload a WAV file containing Morse beeps."
    )

    with st.expander("Example Morse Code"):
        st.markdown("`.... . .-.. .-.. --- / .-- --- .-. .-.. -..` → Hello World")

    morse_input = st.text_area("Manual Morse input", height=140)
    audio_file = st.file_uploader("Upload WAV file", type=["wav"])

    col1, col2 = st.columns(2)
    with col1:
        text_submit = st.button("Translate Text")
    with col2:
        audio_submit = st.button("Translate Audio")

    if text_submit and morse_input:
        try:
            result = submit_text_translation(morse_input)
            render_translation_result(result)
        except requests.RequestException as exc:
            st.error(f"Text translation request failed: {exc}")

    if audio_submit and audio_file is not None:
        try:
            result = submit_audio_translation(audio_file)
            render_translation_result(result)
        except requests.RequestException as exc:
            st.error(f"Audio translation request failed: {exc}")

    if text_submit and not morse_input:
        st.warning("Enter Morse code into the text area before submitting.")

    if audio_submit and audio_file is None:
        st.warning("Upload a WAV file to translate audio input.")

    st.markdown("---")
    st.caption("FastAPI backend expected at http://localhost:8000")


if __name__ == "__main__":
    main()
