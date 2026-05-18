"""FastAPI gateway for text and audio Morse translation endpoints."""

from fastapi import FastAPI, APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.dsp import (
    calculate_rms,
    dynamic_noise_floor,
    extract_morse_from_audio,
    load_audio_file,
)
from app.logger import get_logger
from app.schemas import (
    AudioTranslateResponse,
    TextTranslateRequest,
    TranslationResponse,
)
from app.translator import translate_morse_pipeline, validate_morse_input

app = FastAPI(
    title="Morse Code Interpreter",
    description="A multi-modal Morse code translation service with text and audio endpoints.",
    version="1.0.0",
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/translate-text", response_model=TranslationResponse)
async def translate_text(payload: TextTranslateRequest) -> TranslationResponse:
    """Translate a manual Morse code string into structured text output."""
    try:
        safe_input = validate_morse_input(payload.morse_code)
        return translate_morse_pipeline(safe_input)
    except ValueError as exc:
        logger.warning("Text translation validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error while translating Morse text.")
        raise HTTPException(status_code=500, detail="Internal translation error.")


@router.post("/translate-audio", response_model=AudioTranslateResponse)
async def translate_audio(file: UploadFile = File(...)) -> AudioTranslateResponse:
    """Translate a WAV audio upload containing Morse code into structured text output."""
    if file.content_type not in {"audio/wav", "audio/x-wav", "audio/wave"}:
        raise HTTPException(status_code=400, detail="Only WAV audio uploads are supported.")

    try:
        audio_data = await file.read()
        audio, sample_rate, duration_seconds = load_audio_file(audio_data)
        rms = calculate_rms(audio)
        noise_floor = dynamic_noise_floor(audio)
        morse_code = extract_morse_from_audio(audio, sample_rate)
        translation = translate_morse_pipeline(morse_code)

        response = AudioTranslateResponse(
            translation=translation,
            sample_rate=sample_rate,
            duration_seconds=duration_seconds,
            rms=rms,
            noise_floor=noise_floor,
        )
        logger.info(
            "Audio translation completed: sample_rate=%s duration=%.2f rms=%.4f noise_floor=%.4f",
            sample_rate,
            duration_seconds,
            rms,
            noise_floor,
        )
        return response
    except ValueError as exc:
        logger.warning("Audio translation validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error while translating Morse audio.")
        raise HTTPException(status_code=500, detail="Internal audio translation error.")


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for the Morse Code Interpreter service."""
    return JSONResponse(content={"status": "healthy"})


app.include_router(router)
