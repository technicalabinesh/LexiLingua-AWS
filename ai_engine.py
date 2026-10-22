"""
LexieLingua Unified AI Engine - Groq & OpenAI Multi-Model Provider
NO AZURE DEPENDENCIES.
"""

import os
import io
import re
from typing import Generator, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Model Definitions & Rankings
MODEL_CATALOG = {
    "openai/gpt-oss-120b": {
        "name": "🥇 openai/gpt-oss-120b",
        "description": "Best Overall Model (High Intelligence, Deep Reasoning)",
        "provider": "groq",
        "badge": "Best Overall",
    },
    "openai/gpt-oss-20b": {
        "name": "🥈 openai/gpt-oss-20b",
        "description": "Faster & Cheaper for Simple Tasks",
        "provider": "groq",
        "badge": "Fast & Efficient",
    },
    "qwen/qwen3.8-27b": {
        "name": "🥉 qwen/qwen3.8-27b",
        "description": "Good Alternative (Currently Preview)",
        "provider": "groq",
        "badge": "Preview",
    },
    "gpt-4o": {
        "name": "⚡ OpenAI gpt-4o",
        "description": "Flagship ChatGPT Model (Requires OPENAI_API_KEY)",
        "provider": "openai",
        "badge": "ChatGPT Flagship",
    },
    "gpt-4o-mini": {
        "name": "🚀 OpenAI gpt-4o-mini",
        "description": "Lightweight ChatGPT Model (Requires OPENAI_API_KEY)",
        "provider": "openai",
        "badge": "ChatGPT Fast",
    },
    "allam-2-7b": {
        "name": "🌍 allam-2-7b",
        "description": "Multilingual & Arabic Foundation Model",
        "provider": "groq",
        "badge": "Multilingual",
    },
    "canopylabs/orpheus-v1-english": {
        "name": "🔤 canopylabs/orpheus-v1-english",
        "description": "Specialized English Reasoning Model",
        "provider": "groq",
        "badge": "English Specialized",
    },
    "canopylabs/orpheus-arabic-saudi": {
        "name": "🇸🇦 canopylabs/orpheus-arabic-saudi",
        "description": "Saudi Arabic Specialized Language Model",
        "provider": "groq",
        "badge": "Arabic Specialized",
    },
    "openai/gpt-oss-safeguard-20b": {
        "name": "🛡️ openai/gpt-oss-safeguard-20b",
        "description": "Safeguarded LLM for Content Safety",
        "provider": "groq",
        "badge": "Safeguarded",
    },
    "meta-llama/llama-prompt-guard-2-86m": {
        "name": "🛡️ llama-prompt-guard-2-86m",
        "description": "Prompt Safety Guard Model (86M)",
        "provider": "groq",
        "badge": "Safety Guard",
    },
    "meta-llama/llama-prompt-guard-2-22m": {
        "name": "🛡️ llama-prompt-guard-2-22m",
        "description": "Prompt Safety Guard Model (22M)",
        "provider": "groq",
        "badge": "Safety Guard",
    },
}

WHISPER_MODELS = {
    "whisper-large-v3": "Groq Whisper Large V3 (Highest Accuracy)",
    "whisper-large-v3-turbo": "Groq Whisper Large V3 Turbo (Ultra-Fast)",
}

_GROQ_CLIENT = None
_OPENAI_CLIENT = None
_CURRENT_GROQ_KEY = None
_CURRENT_OPENAI_KEY = None

def get_groq_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        except Exception:
            key = ""
    return key

def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        try:
            import streamlit as st
            key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
        except Exception:
            key = ""
    return key

def is_groq_available() -> bool:
    return bool(get_groq_api_key())

def is_openai_available() -> bool:
    return bool(get_openai_api_key())

def get_groq_client():
    global _GROQ_CLIENT, _CURRENT_GROQ_KEY
    key = get_groq_api_key()
    if not key:
        return None
    if _GROQ_CLIENT is None or _CURRENT_GROQ_KEY != key:
        try:
            from groq import Groq
            _GROQ_CLIENT = Groq(api_key=key)
            _CURRENT_GROQ_KEY = key
        except Exception as exc:
            print(f"[Groq Init Error]: {exc}")
            return None
    return _GROQ_CLIENT

def get_openai_client():
    global _OPENAI_CLIENT
    key = get_openai_api_key()
    if not key:
        return None
    if _OPENAI_CLIENT is None:
        try:
            from openai import OpenAI
            _OPENAI_CLIENT = OpenAI(api_key=key)
        except Exception as exc:
            print(f"[OpenAI Init Error]: {exc}")
            return None
    return _OPENAI_CLIENT

def stream_chat_completion(messages: List[Dict[str, str]], model: str = "openai/gpt-oss-120b") -> Generator[str, None, None]:
    """
    Streams tokens in real-time using Groq or OpenAI client.
    """
    is_openai_model = model.startswith("gpt-4") or model.startswith("gpt-3")
    
    if is_openai_model:
        client = get_openai_client()
        if not client:
            yield f"⚠️ **OpenAI Key Missing:** `OPENAI_API_KEY` is required for `{model}`. Switching to Groq fallback..."
            model = "openai/gpt-oss-120b"
            client = get_groq_client()
    else:
        client = get_groq_client()

    if not client:
        yield "⚠️ **No API Key Configured:** Please set `GROQ_API_KEY` in `.env`."
        return

    try:
        if is_openai_model:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
        else:
            # Using Groq client
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
    except Exception as exc:
        yield f"⚠️ **AI Execution Error ({model}):** `{exc}`"

def summarize_text_ai(text: str, length: str = "Medium", model: str = "openai/gpt-oss-120b") -> Dict[str, Any]:
    """
    Generates structured document summaries using Groq/OpenAI LLM models.
    Truncates text to ~10,000 characters to respect Groq Tokens Per Minute (TPM) limits.
    """
    from utils import word_count, extractive_summary, key_points

    client = get_groq_client() or get_openai_client()
    if not client:
        n = {"Short": 3, "Medium": 6, "Long": 10}.get(length, 6)
        s = extractive_summary(text, num_sentences=n)
        kp = key_points(text, num_points=5)
        return {
            "summary": s,
            "key_points": kp,
            "mode": "Extractive (Offline)",
            "model": "Offline Extractive Engine",
            "original_words": word_count(text),
            "summary_words": word_count(s),
        }

    length_prompt = {
        "Short": "2-3 concise, high-impact sentences",
        "Medium": "1-2 thorough, structured paragraphs",
        "Long": "3-4 detailed, exhaustive sections",
    }.get(length, "1-2 paragraphs")

    # Limit payload to 10,000 characters (~2,000 tokens) to ensure prompt fits safely under Groq 8,000 TPM limit
    safe_text = text[:10000]

    prompt = f"""
You are an advanced document intelligence system.
Task: Provide a structured summary of the following document.
Requirement: {length_prompt}.

Return strictly in this format:
SUMMARY:
<Write summary text here>

KEY POINTS:
- <Key point 1>
- <Key point 2>
- <Key point 3>
- <Key point 4>
- <Key point 5>

DOCUMENT:
{safe_text}
""".strip()

    models_to_try = [model]
    if model != "openai/gpt-oss-20b" and "gpt-oss" in model:
        models_to_try.append("openai/gpt-oss-20b")

    for target_model in models_to_try:
        try:
            res = client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
            )
            raw = res.choices[0].message.content or ""
            summary_text = raw
            points = []
            if "KEY POINTS:" in raw:
                parts = raw.split("KEY POINTS:", 1)
                summary_text = parts[0].replace("SUMMARY:", "").strip()
                points = [
                    line.lstrip("-•* ").strip()
                    for line in parts[1].splitlines()
                    if line.strip() and line.strip().startswith(("-", "•", "*", "1.", "2.", "3.", "4.", "5."))
                ]

            return {
                "summary": summary_text,
                "key_points": points[:5],
                "mode": f"Groq AI ({target_model})",
                "model": target_model,
                "original_words": word_count(text),
                "summary_words": word_count(summary_text),
            }
        except Exception as exc:
            err_msg = str(exc)
            if "413" in err_msg or "rate_limit" in err_msg:
                print(f"[Summarizer AI Notice]: {target_model} TPM limit exceeded. Trying fallback model...")
                continue
            print(f"[Summarizer AI Error]: {exc}")
            break

    # Fallback to extractive
    n = {"Short": 3, "Medium": 6, "Long": 10}.get(length, 6)
    s = extractive_summary(text, num_sentences=n)
    kp = key_points(text, num_points=5)
    return {
        "summary": s,
        "key_points": kp,
        "mode": "Extractive Fallback",
        "model": "Fallback (Extractive Engine)",
        "original_words": word_count(text),
        "summary_words": word_count(s),
    }

def transcribe_audio_ai(file_bytes: bytes, filename: str = "audio.wav", model: str = "Speech Recognition") -> Dict[str, Any]:
    """
    Transcribes audio using Speech Recognition engine (no Groq/Whisper API key required).
    """
    from transcriber import transcribe_audio
    return transcribe_audio(file_bytes=file_bytes, filename=filename, model=model)


