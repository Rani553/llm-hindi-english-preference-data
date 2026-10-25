# Bilingual LLM Preference Dataset (RLHF-style)

A small, carefully labeled **pairwise preference dataset** — the kind of data used to train reward models — built from Hindi, Hinglish and English prompts, plus a test of whether an LLM judge can replace a human labeler.

## What it does
1. **20 prompts** (`prompts.csv`) — 11 English, 5 Hinglish, 4 Hindi — across explanations, advice, technical questions, coding, code review, creative writing, writing, summarization, planning, translation and safety.
2. Gets one response each from **Gemini 2.0 Flash** (model A) and **Llama 3.1 8B Instant via Groq** (model B).
3. Every pair is compared by a human **blind and in random order**, scoring correctness, helpfulness, clarity and language fit (1–5) and picking a winner with a written reason (rules in `guidelines.md`).
4. An **LLM judge runs twice per pair with the order swapped** to measure position bias.
5. Exports the result as `preference_dataset.jsonl` (`prompt`, `chosen`, `rejected`, `reason`, `language`).

## Files
| File | Purpose |
|---|---|
| `prompts.csv` | Prompts with `id`, `category`, `language` |
| `llm.py` | One `ask()` function for Gemini and Groq, with retries |
| `generate.py` | Step 1 — both models answer every prompt → `responses.json` |
| `compare.py` | Step 2 — interactive blind human comparison → `human_prefs.csv` |
| `judge.py` | Step 3 — LLM judge in both orders → `judge_prefs.csv` |
| `report.py` | Step 4 — win rates, scores, judge agreement → `report.md` + `preference_dataset.jsonl` |
| `guidelines.md` | Scoring rubric used by both the human and the judge |

## Key findings
_Not run yet — fill in from `report.md` after step 4:_
- Human labels: model A won __%, model B __%, ties __%
- Biggest gap (dimension / category): …
- Judge gave the same winner in both orders __% of the time (position bias)
- Where the judge and the human disagreed: …

## Run
```bash
pip install -r requirements.txt

# Windows (cmd)
set GEMINI_API_KEY=...
set GROQ_API_KEY=...
# macOS / Linux
export GEMINI_API_KEY=... GROQ_API_KEY=...

python generate.py               # 1. two models answer every prompt
python compare.py                # 2. YOU compare blind (resumable, q to quit)
python judge.py [provider] [model]   # 3. LLM judge, both orders (default: gemini)
python report.py                 # 4. report.md + preference_dataset.jsonl
```
