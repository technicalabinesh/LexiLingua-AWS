"""
Voice & Audio Speech Recognition Module using SpeechRecognition.
Uses Google Speech Recognition (free, no API key required).
"""

import io
from typing import Dict, Any

try:
    import speech_recognition as sr
except ImportError:
    sr = None

def is_speech_recognition_available() -> bool:
    """Returns True if the speech_recognition package is installed."""
    return sr is not None

# Alias for backwards compatibility
is_whisper_available = is_speech_recognition_available

def transcribe_audio(
    file_bytes: bytes,
    filename: str = "audio.wav",
    model: str = "Speech Recognition",
    language: str = "en-US",
) -> Dict[str, Any]:
    """
    Transcribes audio bytes to text using speech_recognition (Google Speech API).
    Requires no API keys and works with microphone and standard audio files.
    """
    if not is_speech_recognition_available():
        return {
            "success": False,
            "error": "The `speech_recognition` package is not installed. Run `pip install SpeechRecognition`.",
            "transcription": "",
        }

    if not file_bytes or len(file_bytes) == 0:
        return {
            "success": False,
            "error": "Audio data stream was empty or disconnected.",
            "transcription": "",
        }

    # Prepare audio buffer
    audio_stream = io.BytesIO(file_bytes)

    # Check if format conversion is needed (speech_recognition requires WAV, AIFF, or FLAC)
    is_wav = filename.lower().endswith(".wav") or file_bytes[:4] == b"RIFF"
    if not is_wav:
        try:
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(io.BytesIO(file_bytes))
            wav_buf = io.BytesIO()
            audio_segment.export(wav_buf, format="wav")
            wav_buf.seek(0)
            audio_stream = wav_buf
        except Exception as conv_err:
            return {
                "success": False,
                "error": (
                    f"Uploaded file '{filename}' could not be converted to WAV. "
                    "Please upload a .wav audio file or record directly using the Live Voice Recorder."
                ),
                "transcription": "",
            }

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_stream) as source:
            # Adjust for ambient noise slightly and record
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language=language)
        return {
            "success": True,
            "transcription": text.strip(),
            "filename": filename,
            "model": "Speech Recognition",
        }
    except sr.UnknownValueError:
        return {
            "success": False,
            "error": "Could not understand audio. Please speak clearly into the microphone.",
            "transcription": "",
        }
    except sr.RequestError as req_err:
        return {
            "success": False,
            "error": f"Speech Recognition service request error: {req_err}",
            "transcription": "",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Audio processing error: {exc}",
            "transcription": "",
        }
