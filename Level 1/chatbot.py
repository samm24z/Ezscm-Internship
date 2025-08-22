#!/usr/bin/env python3
"""
Level 1 — LLM-only smart assistant (prompt engineering focus).

Behavior:
- Always respond step-by-step with clear structure.
- For any direct arithmetic question (e.g., "15 + 23"), REFUSE and hint to a calculator tool.
- Uses OpenAI API if OPENAI_API_KEY is present; otherwise falls back to a lightweight local mock.
- Logs all interactions to logs/level1_log.txt
"""

import os
import re
import sys
from datetime import datetime

# ------------- Minimal optional OpenAI wiring -------------
def call_openai_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Uses OpenAI API if available; otherwise returns a mock response.
    You can install openai: pip install openai
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Local mock: very simple pseudo-reasoning for the demo.
        return local_llm_mock(user_prompt)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)  # type: ignore
        # GPT-4o-mini/4.1-mini are economical options; change as needed.
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM Error / fallback mock] {local_llm_mock(user_prompt)}"

# ------------- Simple mock "LLM" for offline use -------------
def local_llm_mock(user_prompt: str) -> str:
    # Very small knowledge for demo purposes
    lower = user_prompt.lower()
    if "colors in a rainbow" in lower:
        steps = [
            "Recall the acronym VIBGYOR.",
            "List each color from longest to shortest wavelength.",
            "Provide a brief reason it's seen in that order."
        ]
        answer = "- Violet\n- Indigo\n- Blue\n- Green\n- Yellow\n- Orange\n- Red"
        return format_step_by_step(steps, answer)
    if "why the sky is blue" in lower:
        steps = [
            "Sunlight contains many wavelengths.",
            "Air molecules scatter shorter wavelengths more efficiently (Rayleigh scattering).",
            "Blue light (shorter wavelength) is scattered across the sky and reaches our eyes."
        ]
        answer = "Because shorter wavelengths (blue) scatter more in the atmosphere (Rayleigh scattering)."
        return format_step_by_step(steps, answer)
    if "which planet is the hottest" in lower:
        steps = [
            "Compare average surface temperatures of planets.",
            "Note that Venus has a runaway greenhouse effect.",
            "Conclude the hottest planet is Venus."
        ]
        answer = "Venus is the hottest planet in our solar system due to an extreme greenhouse effect."
        return format_step_by_step(steps, answer)
    # default structure
    steps = [
        "Identify the core question.",
        "Recall relevant facts.",
        "Synthesize a concise, structured answer."
    ]
    answer = "Here is a clear, structured answer to your question."
    return format_step_by_step(steps, answer)

def format_step_by_step(steps, final_answer) -> str:
    lines = ["Step-by-step reasoning:"]
    for i, s in enumerate(steps, 1):
        lines.append(f"{i}. {s}")
    lines.append("—")
    lines.append(f"Answer: {final_answer}")
    return "\n".join(lines)

# ------------- Math detection -------------
MATH_PATTERN = re.compile(r"^\s*([-+/*]|\d|\s|what\s+is|add|plus|minus|times|multiply|multiplied|divided|sum|difference|product|quotient)+\?*\s*$", re.IGNORECASE)

def is_direct_math(query: str) -> bool:
    # Treat as direct math if the query is mostly an arithmetic statement or explicitly asks for a calculation.
    return bool(MATH_PATTERN.match(query.strip()))

# ------------- Logging -------------
def log_interaction(path, user, assistant):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] USER: {user}\n")
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] ASSISTANT: {assistant}\n\n")

# ------------- CLI -------------
SYSTEM_PROMPT = """You are a helpful assistant. Always think step-by-step and present a clear, numbered reasoning list followed by a short final answer starting with 'Answer:'. If the user asks for arithmetic like '15 + 23', do NOT compute; instead, politely refuse and suggest using a calculator tool."""

def answer(query: str) -> str:
    if is_direct_math(query):
        return ("I can't compute arithmetic in Level 1.\n"
                "Hint: please use the calculator tool in the next level.")
    return call_openai_llm(SYSTEM_PROMPT, query)

def main():
    print("Level 1 — LLM-only assistant (type 'exit' to quit)")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        if q.lower() in {"exit","quit"}:
            print("Bye!")
            return
        resp = answer(q)
        print(resp, flush=True)
        log_interaction("logs/level1_log.txt", q, resp)

if __name__ == "__main__":
    main()
