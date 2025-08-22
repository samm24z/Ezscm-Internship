#!/usr/bin/env python3
"""
Very simple English→German translator tool for demo.
- Contains a small phrase dictionary and a naive capitalization rule.
- In a real app, you'd call a translation API.
"""

PHRASES = {
    "good morning": "Guten Morgen",
    "have a nice day": "Einen schönen Tag noch",
    "sunshine": "Sonnenschein",
    "hello": "Hallo",
    "hi": "Hallo",
}

def translate_en_to_de(text: str) -> str:
    key = text.strip().lower()
    if key in PHRASES:
        return PHRASES[key]
    # naive word-by-word fallback (super minimal for demo)
    words = key.split()
    if not words:
        return ""
    # Super crude mapping
    mapping = {
        "good": "gut",
        "morning": "Morgen",
        "have": "haben",
        "a": "ein",
        "nice": "schön",
        "day": "Tag",
        "and": "und",
        "then": "dann",
        "translate": "übersetzen",
    }
    out = " ".join(mapping.get(w, w) for w in words)
    # Capitalize first letter to resemble German sentence capitalization
    return out[:1].upper() + out[1:]
