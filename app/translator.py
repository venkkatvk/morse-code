"""Morse validation, decoding, lookup, and Pydantic AI orchestration."""

import re
from typing import Dict
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.logger import get_logger
from app.schemas import TranslationResponse

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
}

ALLOWED_MORSE_PATTERN = re.compile(r"^[\.\-\s/]+$")

# =====================================================================
# 🧠 THE COGNITIVE REVOLUTION: PYDANTIC AI AGENT DEFINITION
# =====================================================================

# 1. Initialize the model provider (Ensure OPENAI_API_KEY is in your environment)
llm_model = OpenAIModel('gpt-4o')

# 2. Define the Agent with its Strict System Blueprint and Structured Result Contract
morse_agent = Agent(
    model=llm_model,
    result_type=TranslationResponse,  # Forces output into our strict Pydantic box!
    system_prompt=(
        "You are an elite telecommunications decryption agent specializing in Morse code correction. "
        "You will receive a raw text that was literally translated from Morse code. "
        "Your duty is to perform semantic smoothing, correct spelling errors caused by missing signals, "
        "and properly capitalize the sentences into beautiful, fluent English. "
        "If the input contains too many unresolved symbols ('?'), deduce the text from context, "
        "flag 'is_corrupted' as true, and adjust the 'confidence_score' accordingly."
    )
)

# 3. Register our Deterministic Lookup Tool directly to the Agent's runtime environment!
@morse_agent.tool
def deterministic_dictionary_tool(ctx, morse_code_chunk: str) -> str:
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
    # Step 1: Input Validation Gate
    normalized_morse = validate_morse_input(morse_code)
    
    try:
        logger.info("Engaging Pydantic AI Cognitive Run...")
        
        # Step 2: Synchronously run the agent. 
        # The agent will automatically invoke the 'deterministic_dictionary_tool' if it needs it!
        result = morse_agent.run_sync(
            f"Please translate and smooth this raw Morse code stream: {normalized_morse}"
        )
        
        # 'result.data' is guaranteed to be an instance of TranslationResponse!
        return result.data

    except Exception as exc:
        logger.exception("Pydantic AI engine faulted, executing graceful fallback protocol.")
        
        # Step 3: Graceful Degradation / Fallback Gate
        from decode_logic import decode_morse # fall back to manual decoding if LLM fails completely
        raw_decoded = "".join([MORSE_CODE_DICT.get(c, "?") for c in normalized_morse.split() if c])
        
        return TranslationResponse(
            translated_text=f"[FALLBACK LOGIC]: {raw_decoded}",
            confidence_score=0.10,
            is_corrupted=True
        )
