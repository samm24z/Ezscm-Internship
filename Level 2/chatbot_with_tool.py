#!/usr/bin/env python3
"""
Level 2 — LLM + Basic Tool (Calculator).
Behavior:
- Detect basic arithmetic queries and route to calculator_tool (do NOT compute inside LLM).
- Non-math queries go to the LLM directly.
- Multi-step mixed queries should gracefully say it's not supported yet (per spec).
- Logs all interactions to logs/level2_log.txt
"""

import os
import re
from datetime import datetime

import calculator_tool

# --- Optional LLM (same pattern as level 1) ---
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
    except Exception as e:
        return f"[LLM Error / fallback mock] {local_llm_mock(user_prompt)}"

def local_llm_mock(user_prompt: str) -> str:
    return "Answer: " + ("Paris" if "capital of france" in user_prompt.lower() else "Here is a concise answer.")

SYSTEM_PROMPT = """You are a helpful assistant. For non-math questions, answer clearly and concisely. For math, the PROGRAM will call tools, not you."""

# --- Detection helpers ---
MATH_KEYWORDS = re.compile(r"\b(add|plus|sum|times|multiply|multiplied|product|minus|difference|divided|/|\*|\+|\-|\bx\b|×)\b", re.IGNORECASE)

def looks_like_math(q: str) -> bool:
    # If the query mentions clear math keywords or looks like "a op b"
    if calculator_tool.NUM_OP_NUM.match(q.strip()):
        return True
    return bool(MATH_KEYWORDS.search(q))

def is_mixed_query(q: str) -> bool:
    # crude heuristic: asks both math and non-math facts
    has_math = looks_like_math(q)
    has_fact = any(k in q.lower() for k in ["capital", "who is", "what is the capital of", "tell me the capital"])
    return has_math and has_fact

def log(path, user, assistant):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] USER: {user}\n")
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] ASSISTANT: {assistant}\n\n")

def handle_query(q: str) -> str:
    if is_mixed_query(q):
        return "I can do a single task at a time at Level 2. Multi-step mixed queries aren't supported yet."
    if looks_like_math(q):
        # try explicit patterns first
        m = calculator_tool.NUM_OP_NUM.match(q.strip())
        try:
            if m:
                result = calculator_tool.calculate(q)
                return f"Calculator result: {result:g}"
            # basic verb patterns
            lower = q.lower()
            if "times" in lower or "multiply" in lower or "multiplied" in lower:
                # extract two numbers
                nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", q)]
                if len(nums) >= 2:
                    return f"Calculator result: {calculator_tool.multiply(nums[0], nums[1]):g}"
            if "add" in lower or "plus" in lower or "sum" in lower:
                nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", q)]
                if len(nums) >= 2:
                    return f"Calculator result: {calculator_tool.add(nums[0], nums[1]):g}"
        except Exception as e:
            return f"Sorry, I couldn't compute that: {e}"
        return "Please provide a simple expression like '12 * 7' or 'Add 45 and 30'."
    # Non-math → LLM
    return call_openai_llm(SYSTEM_PROMPT, q)

def main():
    print("Level 2 — LLM + Calculator Tool (type 'exit' to quit)")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        if q.lower() in {"exit","quit"}:
            print("Bye!")
            return
        resp = handle_query(q)
        print(resp, flush=True)
        log("logs/level2_log.txt", q, resp)

if __name__ == "__main__":
    main()
