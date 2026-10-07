"""
Document Summarizer & Intelligence Module.
NO AZURE DEPENDENCIES.
"""

from typing import Dict, Any, Generator
from ai_engine import (
    summarize_text_ai,
    is_groq_available,
    is_openai_available,
    stream_chat_completion,
)
from utils import extractive_summary, key_points, word_count

def is_ai_mode_available() -> bool:
    return is_groq_available() or is_openai_available()

def summarize_offline(text: str, length: str = "Medium") -> Dict[str, Any]:
    counts = {"Short": 3, "Medium": 6, "Long": 10}
    n = counts.get(length, 6)
    summary = extractive_summary(text, num_sentences=n)
    points = key_points(text, num_points=5)

    return {
        "summary": summary,
        "key_points": points,
        "mode": "Extractive (Offline)",
        "model": "Offline Algorithm",
        "original_words": word_count(text),
        "summary_words": word_count(summary),
    }

def summarize(text: str, length: str = "Medium", model: str = "openai/gpt-oss-120b") -> Dict[str, Any]:
    """
    Summarizes document text using Groq/OpenAI LLM models or offline fallback.
    """
    if not is_ai_mode_available():
        return summarize_offline(text, length)

    return summarize_text_ai(text=text, length=length, model=model)

def stream_summarize(text: str, length: str = "Medium", model: str = "openai/gpt-oss-120b") -> Generator[str, None, None]:
    """
    Streams summary tokens in real-time.
    """
    if not is_ai_mode_available():
        res = summarize_offline(text, length)
        yield res.get("summary", "")
        return

    length_prompt = {
        "Short": "1 concise paragraph with essential takeaways",
        "Medium": "2-3 well-structured paragraphs with main concepts",
        "Long": "3-4 detailed, exhaustive sections",
    }.get(length, "2-3 well-structured paragraphs")

    safe_text = text[:10000]
    prompt = f"You are an expert document summarizer. Summarize the following text clearly with depth ({length_prompt}):\n\n{safe_text}"
    messages = [{"role": "user", "content": prompt}]
    
    for token in stream_chat_completion(messages, model=model):
        yield token