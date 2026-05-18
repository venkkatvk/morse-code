Act as a Principal AI Infrastructure Engineer and Full-Stack Python Developer. Write a complete, production-grade, single-file Python application that implements the entire Morse Code Interpreter architecture discussed. 

The codebase must include:
1. Data Layer: A Pydantic V2 model for the output schema containing fields for translated_text (str), confidence_score (float), and is_corrupted (bool).
2. Processing Layer: A local Python regex function to reject non-Morse inputs, and a Digital Signal Processing (DSP) function using scipy.io.wavfile to calculate a dynamic audio noise floor using Root Mean Square (RMS) to extract dots and dashes from peak durations.
3. Orchestration Layer: A FastAPI application exposing two distinct POST endpoints: `/translate-text` (JSON payload) and `/translate-audio` (multipart form file upload). Both endpoints must route validated data to a unified internal function that runs a mock tool-calling dictionary lookup and an LLM contextual refinement step. Include a try-except block to return a raw fallback translation with a warning flag if the LLM step fails.
4. Interface Layer: A clean Streamlit frontend application providing a text area for manual Morse code strings, a file uploader for .wav files, and a submission mechanism that triggers the respective FastAPI endpoint and displays the final pristine paragraph along with the metadata payload.

Ensure the code is clean, fully type-hinted, modular, and completely documented with standard industry logging.