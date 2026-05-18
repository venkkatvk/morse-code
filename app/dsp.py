"""Audio preprocessing and Morse extraction utilities."""

import io
from typing import Tuple

import numpy as np
from scipy.io import wavfile


def load_audio_file(file_bytes: bytes) -> Tuple[np.ndarray, int, float]:
    """Load WAV audio bytes and return mono signal, sample rate, and duration."""
    buffer = io.BytesIO(file_bytes)
    sample_rate, audio = wavfile.read(buffer)
    if sample_rate <= 0:
        raise ValueError("Invalid sample rate in uploaded audio file.")

    if audio.ndim > 1:
        audio = np.mean(audio.astype(np.float64), axis=1)
    else:
        audio = audio.astype(np.float64)

    duration_seconds = float(audio.shape[0] / sample_rate)
    return audio, sample_rate, duration_seconds


def calculate_rms(signal: np.ndarray) -> float:
    """Calculate the root mean square of an audio signal."""
    signal = signal.astype(np.float64)
    return float(np.sqrt(np.mean(np.square(signal))))


def dynamic_noise_floor(signal: np.ndarray) -> float:
    """Estimate a dynamic noise floor from the audio signal."""
    rms = calculate_rms(signal)
    percentile_noise = float(np.percentile(np.abs(signal), 10))
    return float(max(rms * 0.15, percentile_noise))


def extract_morse_from_audio(audio: np.ndarray, sample_rate: int) -> str:
    """Extract a Morse code string from raw audio signal using duration heuristics."""
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive.")

    abs_signal = np.abs(audio)
    if abs_signal.max() == 0.0:
        raise ValueError("Uploaded audio contains no audible signal.")

    noise_floor = dynamic_noise_floor(audio)
    normalized = abs_signal / abs_signal.max()
    threshold = float(max(noise_floor / abs_signal.max(), 0.08))

    window_ms = 20
    window_size = max(1, int(sample_rate * window_ms / 1000))
    envelope = np.array(
        [normalized[i : i + window_size].max() for i in range(0, len(normalized), window_size)]
    )
    active = envelope > threshold

    durations = []
    current = active[0]
    length = 0
    for state in active:
        if state == current:
            length += 1
        else:
            durations.append((current, length * window_ms / 1000.0))
            current = state
            length = 1
    durations.append((current, length * window_ms / 1000.0))

    if not durations:
        raise ValueError("Unable to extract Morse signal from audio.")

    symbols = []
    for is_tone, duration in durations:
        if is_tone:
            symbols.append(".") if duration < 0.18 else symbols.append("-")
        else:
            if duration >= 0.5:
                symbols.append(" / ")
            elif duration >= 0.18:
                symbols.append(" ")

    morse_code = "".join(symbols).strip()
    if not morse_code:
        raise ValueError("No Morse code pattern found in audio.")

    return " ".join(morse_code.split())
