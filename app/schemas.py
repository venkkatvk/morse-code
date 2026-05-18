"""Pydantic models for request validation and structured translation output."""

from pydantic import BaseModel, Field
from typing import Literal


class TranslationResponse(BaseModel):
    """Structured response for Morse translation results."""

    translated_text: str = Field(..., description="The decoded natural language output.")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence in the translation output."
    )
    is_corrupted: bool = Field(
        False,
        description="Whether the final output fell back from the LLM refinement stage."
    )


class TextTranslateRequest(BaseModel):
    """Request payload for text-based Morse translation."""

    morse_code: str = Field(..., min_length=1, max_length=5000)
    modality: Literal["text"] = Field("text", description="Request modality type.")


class AudioTranslateResponse(BaseModel):
    """Response wrapper for audio translation metadata."""

    translation: TranslationResponse
    sample_rate: int
    duration_seconds: float
    rms: float
    noise_floor: float
