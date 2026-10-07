"""
Document extraction and text processing utilities.
"""

import io
import re
from collections import Counter
import docx
from pypdf import PdfReader

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before
being below between both but by can't cannot could couldn't did didn't do does doesn't doing
don't down during each few for from further had hadn't has hasn't have haven't having he he'd
he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in
into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on
once only or other ought our ours ourselves out over own same shan't she she'd she'll she's
should shouldn't so some such than that that's the their theirs them themselves then there
there's these they they'd they'll they're they've this those through to too under until up
very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's
which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've
your yours yourself yourselves
""".split())

def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported format.")

def extractive_summary(text: str, num_sentences: int = 6) -> str:
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", re.sub(r"\s+", " ", text).strip())
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    words = [w for w in re.findall(r"[a-zA-Z']+", text.lower()) if w not in STOPWORDS and len(w) > 2]
    freqs = Counter(words)
    max_f = max(freqs.values()) if freqs else 1
    normalized = {w: f / max_f for w, f in freqs.items()}

    scored = []
    for idx, s in enumerate(sentences):
        tokens = re.findall(r"[a-zA-Z']+", s.lower())
        score = (sum(normalized.get(t, 0.0) for t in tokens) / max(len(tokens), 1)) * (1.15 if idx < 3 else 1.0)
        scored.append((idx, score))

    top_idx = sorted([i for i, _ in sorted(scored, key=lambda x: x[1], reverse=True)[:num_sentences]])
    return " ".join(sentences[i] for i in top_idx)

def key_points(text: str, num_points: int = 5):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text) if len(s.strip()) > 20]
    words = [w for w in re.findall(r"[a-zA-Z']+", text.lower()) if w not in STOPWORDS]
    freqs = Counter(words)
    scored = [(sum(freqs.get(w, 0) for w in re.findall(r"[a-zA-Z']+", s.lower())) / max(len(s.split()), 1), s) for s in sentences]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [s for _, s in scored[:num_points]]

def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))