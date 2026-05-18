<<<<<<< HEAD
# Morse Code Interpreter

A production-style multi-modal Morse Code Interpreter built with FastAPI, Pydantic V2, SciPy DSP audio processing, and Streamlit.

## Features

- `POST /translate-text` for manual Morse code translation
- `POST /translate-audio` for WAV audio uploads containing Morse beeps
- DSP-based audio analysis with RMS and dynamic noise floor
- Mock tool lookup and LLM-style refinement with safe fallback
- Streamlit frontend for text input and WAV upload
- Structured Pydantic output schema with confidence scoring

## Project Structure

- `app/`
  - `api.py` - FastAPI application and endpoint definitions
  - `schemas.py` - Strict Pydantic V2 request and response models
  - `dsp.py` - Audio loading, RMS, noise floor, and Morse extraction logic
  - `translator.py` - Morse validation, decoding, mock tool lookup, refinement, and fallback handling
  - `logger.py` - Structured logger configuration
- `frontend/`
  - `streamlit_app.py` - Streamlit UI for manual Morse input and audio uploads
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.11+ recommended
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Backend

Start the FastAPI service:

```bash
uvicorn app.api:app --reload
```

The API will be available at `http://localhost:8000`.

### Health Check

```bash
curl http://localhost:8000/health
```

## Run the Frontend

Start the Streamlit UI:

```bash
streamlit run frontend/streamlit_app.py
```

Open the Streamlit page shown in the terminal to interact with the application.

## API Endpoints

### Translate Text

- URL: `POST http://localhost:8000/translate-text`
- Payload:

```json
{
  "morse_code": ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
  "modality": "text"
}
```

### Translate Audio

- URL: `POST http://localhost:8000/translate-audio`
- Form field: `file` with WAV audio

## Example Usage

Manual Morse text:

```text
.... . .-.. .-.. --- / .-- --- .-. .-.. -..
```

This should decode roughly to `Hello World` and return a structured translation response.

## Notes

- The audio path expects clean Morse audio in WAV format.
- The refinement stage is a mock LLM simulation with fallback behavior for invalid or low-confidence text.
- The application is intentionally modular for maintainability and future extension.

## License

MIT License
=======
# New-1
>>>>>>> 3bf94e22527237865237e2e06716f107e7fa2e4e
