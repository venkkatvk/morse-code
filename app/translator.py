"""Morse validation, decoding, lookup, and refinement orchestration."""

import re
from typing import Dict

from app.logger import get_logger
from app.schemas import TranslationResponse

logger = get_logger(__name__)

MORSE_CODE_DICT: Dict[str, str] = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-.-.-": ".",
    "--..--": ",",
    "..--..": "?",
    ".----.": "'",
    "-.-.--": "!",
    "-..-.": "/",
    "-.--.-": ")",
    "-.--.": "(",
    ".-...": "&",
    "---...": ":",
    "-.-.-.": ";",
    "-...-": "=",
    ".-.-.": "+",
    "-....-": "-",
    "..--.-": "_",
    ".-..-.": '"',
    ".--.-.": "@",
}

ALLOWED_MORSE_PATTERN = re.compile(r"^[\.\-\s/]+$")


def validate_morse_input(morse_code: str) -> str:
    """Validate and normalize user-supplied Morse code text."""
    cleaned = morse_code.strip()
    if not cleaned:
        raise ValueError("Morse code input cannot be empty.")

    if not ALLOWED_MORSE_PATTERN.match(cleaned):
        raise ValueError(
            "Input contains invalid characters for Morse code. Use only dots, dashes, spaces, and '/' separators."
        )

    normalized = re.sub(r"\s+", " ", cleaned)
    normalized = re.sub(r"\s*/\s*", " / ", normalized)
    return normalized.strip()


def decode_morse(morse_code: str) -> str:
    """Translate normalized Morse code into plaintext."""
    words = [word.strip() for word in morse_code.split("/")]
    decoded_words = []
    for word in words:
        if not word:
            continue
        characters = [code.strip() for code in word.split(" ") if code.strip()]
        decoded = []
        for char_code in characters:
            decoded.append(MORSE_CODE_DICT.get(char_code, "?"))
        decoded_words.append("".join(decoded))

    return " ".join(decoded_words)


def mock_tool_lookup(decoded_text: str) -> str:
    """Simulate a tool-calling lookup that cleans up simple Morse translations."""
    cleaned = decoded_text.replace("?", "").strip()
    if not cleaned:
        return decoded_text
    return cleaned


def mock_llm_refine(decoded_text: str) -> str:
    """Simulate an LLM refinement pass that produces natural language output."""
    refined = decoded_text.strip()
    if not refined:
        raise RuntimeError("LLM refinement could not produce a result.")

    if len(refined) <= 2:
        raise RuntimeError("Refinement failed due to insufficient context.")

    refined = refined.capitalize()
    if refined[-1] not in ".!?":
        refined = f"{refined}."

    return refined


def translate_morse_pipeline(morse_code: str) -> TranslationResponse:
    """Translate Morse code through validation, lookup, and refinement."""
    normalized = validate_morse_input(morse_code)
    decoded = decode_morse(normalized)
    lookup_text = mock_tool_lookup(decoded)

    try:
        final_text = mock_llm_refine(lookup_text)
        confidence = 0.92
        is_corrupted = False
    except Exception as exc:
        logger.exception("LLM refinement failed, returning fallback translation.")
        final_text = lookup_text
        confidence = 0.38
        is_corrupted = True

    return TranslationResponse(
        translated_text=final_text,
        confidence_score=confidence,
        is_corrupted=is_corrupted,
    )
