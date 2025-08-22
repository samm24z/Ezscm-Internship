# Python Software Engineer Assignment — LLM + Agentic Thinking (Basic Implementation)

This repo contains a **minimal, clean** implementation for all three levels of the assignment.

> Designed to run **offline** by default (mock LLM + tiny translator), and automatically switch to **OpenAI** if you set `OPENAI_API_KEY`.

## Structure

```
chatbot.py                # Level 1 — LLM-only (refuse math)
calculator_tool.py        # Tool shared by L2/L3
chatbot_with_tool.py      # Level 2 — LLM + Calculator (one tool)
translator_tool.py        # Tool for L3 (EN->DE, tiny demo dictionary)
full_agent.py             # Level 3 — Full agent (multi-step + memory)
logs/
  level1_log.txt
  level2_log.txt
  level3_log.txt
```

## Quick Start

1) (Optional) Install deps for real LLM access
```bash
pip install openai
export OPENAI_API_KEY=YOUR_KEY
```
> Without a key, the programs will use a **local mock** that’s good enough for the assignment scenarios.

2) Run each level
```bash
python chatbot.py
python chatbot_with_tool.py
python full_agent.py
```

## What each level does

### Level 1 — LLM-only
- Always answers **step-by-step**.
- **Refuses** to compute arithmetic (e.g., "15 + 23") and hints to the calculator tool.
- Example prompts:
  - "What are the colors in a rainbow?"
  - "Tell me why the sky is blue?"
  - "Which planet is the hottest?"
  - "What is 15 + 23?" → refusal

### Level 2 — LLM + Calculator tool
- Detects math and routes to `calculator_tool` (no LLM math).
- Non-math facts go to the LLM.
- Mixed multi-step like "Multiply 9 and 8, and also tell me the capital of Japan" → **graceful failure** message (per spec).

### Level 3 — Full Agent (multi-step + memory)
- Splits a query into **steps** (translate / add / multiply / capitals / generic fact).
- Calls multiple tools (`calculator_tool`, `translator_tool`).
- Maintains a short **memory** of step results and prints a summary.

## Interaction Logs
Logs are appended to `logs/levelX_log.txt`. You can clear them by deleting the files.

## Notes
- `translator_tool.py` is intentionally tiny (dictionary + naive fallback) to keep the solution simple.
- Swap in your favorite LLM by editing `call_openai_llm` functions.
- All files are lightweight and readable so you can extend quickly.
```

