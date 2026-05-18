"""Morse validation, decoding, lookup, and Pydantic AI orchestration."""
"""Morse validation, decoding, lookup, and Pydantic AI orchestration."""

import re
from typing import Dict
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.logger import get_logger
from app.schemas import TranslationResponse

OpenAIModel = _OpenAIModel

logger = get_logger(__name__)

MORSE_CODE_DICT: Dict[str, str] = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6",
    "--...": "7", "---..": "8", "----.": "9", ".-.-.-": ".",
    "--..--": ",", "..–..": "?", ".----.": "'", "-.-.–": "!",
    "-..-.": "/", "-.--.-": ")", "-.--.": "(", ".-...": "&",
    "---...": ":", "-.-.-.": ";", "-...-": "=", ".-.-.": "+",
    "-....-": "-", "..--.-": "_", ".-..-.": '"', ".--.-.": "@",
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2",
    "...--": "3", "....-": "4", ".....": "5", "-....": "6",
    "--...": "7", "---..": "8", "----.": "9", ".-.-.-": ".",
    "--..--": ",", "..–..": "?", ".----.": "'", "-.-.–": "!",
    "-..-.": "/", "-.--.-": ")", "-.--.": "(", ".-...": "&",
    "---...": ":", "-.-.-.": ";", "-...-": "=", ".-.-.": "+",
    "-....-": "-", "..--.-": "_", ".-..-.": '"', ".--.-.": "@",
}

ALLOWED_MORSE_PATTERN = re.compile(r"^[\.\-\s/]+$")

# =====================================================================
# 🧠 THE COGNITIVE REVOLUTION: PYDANTIC AI AGENT DEFINITION
# =====================================================================

llm_model = OpenAIModel('gpt-4o')

morse_agent = Agent(
    model=llm_model,
    result_type=TranslationResponse,
    system_prompt=(
        "You are an elite telecommunications decryption agent specializing in Morse code correction. "
        "You will receive a raw Morse code stream of dots, dashes, and slashes. "
        "You MUST first invoke your 'deterministic_dictionary_tool' to get the literal character lookup. "
        "Once you receive the raw translation back from the tool, perform semantic smoothing, "
        "correct any spelling errors caused by corrupted or missing signals, and properly format "
        "the output sentences into clean, fluent, capitalized English. "
        "If the tool output contains too many unresolved characters ('?'), use your linguistic context "
        "to deduce the intended word, flag 'is_corrupted' as true, and lower your 'confidence_score' accordingly."
    )
)

# Fixed: Removed unused 'ctx' parameter to ensure type-safe tool registry
@morse_agent.tool
def deterministic_dictionary_tool(morse_code_chunk: str) -> str:
    """A deterministic character-by-character dictionary lookup tool for Morse code."""
    words = [word.strip() for word in morse_code_chunk.split("/")]
    decoded_words = []
    for word in words:
        if not word:
            continue
        characters = [code.strip() for code in word.split(" ") if code.strip()]
        decoded = [MORSE_CODE_DICT.get(char_code, "?") for char_code in characters]
        decoded_words.append("".join(decoded))
    return " ".join(decoded_words)


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


def translate_morse_pipeline(morse_code: str) -> TranslationResponse:
    """Translate Morse code through validation and our live Pydantic AI Agent."""
    normalized_morse = validate_morse_input(morse_code)
    
    try:
        logger.info("Engaging Pydantic AI Cognitive Run...")
        result = morse_agent.run_sync(
            f"Please translate and smooth this raw Morse code stream: {normalized_morse}"
        )
        return result.data

    except Exception as exc:
        logger.exception("Pydantic AI engine faulted, executing graceful fallback protocol.")
        
        # Fixed: Removed the non-existent 'decode_logic' import module completely.
        words = [w.strip() for w in normalized_morse.split("/")]
        raw_decoded_words = []
        for word in words:
            chars = [c.strip() for c in word.split(" ") if c.strip()]
            raw_decoded_words.append("".join([MORSE_CODE_DICT.get(c, "?") for c in chars]))
        raw_decoded = " ".join(raw_decoded_words)
        
        return TranslationResponse(
            translated_text=f"[FALLBACK LOGIC]: {raw_decoded}",
            confidence_score=0.10,
            is_corrupted=True
        )