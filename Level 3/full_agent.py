#!/usr/bin/env python3
"""
Level 3 — Full Agentic AI with multi-step tasks.
- Break a query into steps
- Call multiple tools (calculator, translator)
- Maintain short-term memory of step outputs
- Log full history to logs/level3_log.txt
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any

import calculator_tool
import translator_tool

# --- Optional LLM stub for knowledge questions ---
def call_openai_llm(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return local_llm_mock(user_prompt)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)  # type: ignore
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return local_llm_mock(user_prompt)

def local_llm_mock(prompt: str) -> str:
    if "capital of italy" in prompt.lower():
        return "Rome"
    if "distance between earth and mars" in prompt.lower():
        return "It varies widely (about 54.6 million km at closest to over 400 million km)."
    return "Here is a concise answer."

SYSTEM_PROMPT = "You are an agent that completes multi-step tasks by describing each step and keeping a brief memory."

# --- Utilities ---
def log(path, user, assistant):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] USER: {user}\n")
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] ASSISTANT: {assistant}\n\n")

def detect_steps(query: str) -> List[Dict[str, Any]]:
    """
    Very simple, rule-based step detector.
    Recognizes: translate <text> into German; add A and B; multiply A and B; 'capital of X'; generic question.
    """
    q = query.strip()
    lower = q.lower()

    steps: List[Dict[str, Any]] = []

    # Look for translate commands
    t_match = re.search(r"translate\s+'([^']+)'\s+into\s+german", lower)
    if t_match:
        steps.append({"type":"translate", "text": t_match.group(1)})

    # Additions
    add_match = re.search(r"\badd\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)", lower)
    if add_match:
        steps.append({"type":"add", "a": float(add_match.group(1)), "b": float(add_match.group(2))})

    # Multiplications
    mul_match = re.search(r"\bmultiply\s+(-?\d+(?:\.\d+)?)\s+and\s+(-?\d+(?:\.\d+)?)", lower)
    if mul_match:
        steps.append({"type":"multiply", "a": float(mul_match.group(1)), "b": float(mul_match.group(2))})

    # Capitals
    cap_match = re.search(r"capital of\s+([a-zA-Z]+)", lower)
    if cap_match:
        country = cap_match.group(1)
        steps.append({"type":"fact", "question": f"What is the capital of {country}?"})

    # Distance Earth-Mars or other general
    if "distance between earth and mars" in lower:
        steps.append({"type":"fact", "question": "What is the distance between Earth and Mars?"})

    # If nothing matched, treat as a single fact query
    if not steps:
        steps.append({"type":"fact", "question": q})

    return steps

def run_steps(steps: List[Dict[str, Any]]) -> str:
    memory: Dict[str, Any] = {}
    transcript: List[str] = []
    for idx, step in enumerate(steps, 1):
        if step["type"] == "add":
            result = calculator_tool.add(step["a"], step["b"])
            memory[f"step{idx}"] = result
            transcript.append(f"Step {idx}: Add {step['a']} and {step['b']} -> {result:g}")
        elif step["type"] == "multiply":
            result = calculator_tool.multiply(step["a"], step["b"])
            memory[f"step{idx}"] = result
            transcript.append(f"Step {idx}: Multiply {step['a']} and {step['b']} -> {result:g}")
        elif step["type"] == "translate":
            result = translator_tool.translate_en_to_de(step["text"])
            memory[f"step{idx}"] = result
            transcript.append(f"Step {idx}: Translate '{step['text']}' to German -> {result}")
        elif step["type"] == "fact":
            result = call_openai_llm(SYSTEM_PROMPT, step["question"])
            memory[f"step{idx}"] = result
            transcript.append(f"Step {idx}: LLM fact lookup: '{step['question']}' -> {result}")
        else:
            transcript.append(f"Step {idx}: Unknown step type '{step['type']}' (skipped).")

    # Final summary
    summary_lines = ["\nSummary:"]
    for k in sorted(memory.keys()):
        summary_lines.append(f"- {k}: {memory[k]}")
    return "\n".join(transcript + summary_lines)

def main():
    print("Level 3 — Full Agent (type 'exit' to quit)")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        if q.lower() in {"exit","quit"}:
            print("Bye!")
            return
        steps = detect_steps(q)
        result = run_steps(steps)
        print(result, flush=True)
        log("logs/level3_log.txt", q, result)

if __name__ == "__main__":
    main()
