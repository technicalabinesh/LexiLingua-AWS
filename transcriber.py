"""
Voice & Audio Speech Recognition Module using Groq Whisper.
Supports whisper-large-v3 and whisper-large-v3-turbo.
"""

from typing import Dict, Any
from ai_engine import transcribe_audio_ai, is_groq_available

def is_whisper_available() -> bool:
    return is_groq_available()

def transcribe_audio(file_bytes: bytes, filename: str = "audio.wav", model: str = "whisper-large-v3") -> Dict[str, Any]:
    """
    Transcribes audio bytes to text using Groq Whisper (whisper-large-v3 or whisper-large-v3-turbo).
    """
    if not is_whisper_available():
        return {
            "success": False,
            "error": "GROQ_API_KEY is missing. Please configure it in .env to use Whisper transcription.",
            "transcription": "",
        }
    return transcribe_audio_ai(file_bytes=file_bytes, filename=filename, model=model)

