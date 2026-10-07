"""
Ultra-fast Groq & ChatGPT Conversational Engine.
NO AZURE DEPENDENCIES.
"""

from typing import Generator, List, Dict, Any
from ai_engine import (
    stream_chat_completion,
    is_groq_available,
    is_openai_available,
    MODEL_CATALOG,
)

FAQ_KNOWLEDGE_BASE = [
    {"topic": "Admissions", "keywords": ["admission", "enrollment", "application"]},
    {"topic": "Exams & Grades", "keywords": ["exam", "gpa", "results", "revaluation"]},
    {"topic": "Fees & Aid", "keywords": ["fee", "tuition", "scholarship", "financial aid"]},
    {"topic": "Library", "keywords": ["library", "borrow", "e-book", "journal"]},
    {"topic": "Wellbeing", "keywords": ["stress", "anxiety", "counseling", "mental health"]},
]

def is_ai_mode_available() -> bool:
    return is_groq_available() or is_openai_available()

def stream_answer(question: str, history: List[Dict[str, Any]], model: str = "openai/gpt-oss-120b") -> Generator[str, None, None]:
    """
    Streams tokens in real-time with ultra-low latency using Groq / ChatGPT models.
    """
    system_prompt = f"""
You are LexieLingua, a brilliant, unrestricted, and highly versatile AI Assistant powered by {model}.

Guidelines & Output Format:
1. When answering coding or technical questions, format your response in this exact 2-part structure:
   - Part 1: Provide clean, complete, production-grade, fully working code with top docstrings (`#!/usr/bin/env python3`, filename, description, author, type hints, and unittest suite).
   - Part 2: Add a section titled `### How it works` with:
     - Numbered main points highlighting key classes, functions, and helpers with inline code tags (e.g. `Node`, `__slots__`, `reverse`).
     - Sub-bullet points explaining internal mechanics step-by-step (e.g., `prev`, `cur`, `nxt`).
     - Bullet points listing test coverage details.
     - A warm, friendly sign-off (e.g., "Feel free to extend... Happy coding!").
2. For non-coding questions, be direct, engaging, intelligent, and present structured, beautifully styled Markdown answers.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    
    # Keep last 10 turns for memory & fast context processing
    for msg in history[-10:]:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ["user", "assistant"]:
            messages.append({"role": role, "content": content})
            
    messages.append({"role": "user", "content": question})

    for token in stream_chat_completion(messages, model=model):
        yield token

def get_answer(question: str, history: List[Dict[str, Any]], model: str = "openai/gpt-oss-120b") -> str:
    """Non-streaming helper function."""
    full_text = ""
    for token in stream_answer(question, history, model=model):
        full_text += token
    return full_text