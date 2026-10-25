"""Step 1: get one response from each model for every prompt -> responses.json
Usage: python generate.py      (uses MODEL_A / MODEL_B below)"""
import csv, json, os
from llm import ask

MODEL_A = ("gemini", "gemini-2.0-flash")
MODEL_B = ("groq", "llama-3.1-8b-instant")

prompts = list(csv.DictReader(open("prompts.csv", encoding="utf-8")))
data = json.load(open("responses.json", encoding="utf-8")) if os.path.exists("responses.json") else {}
for p in prompts:
    if p["id"] in data:
        continue
    print(f"[{p['id']}] {p['prompt'][:60]}")
    data[p["id"]] = {"A": {"model": f"{MODEL_A[0]}:{MODEL_A[1]}", "text": ask(p["prompt"], *MODEL_A)},
                     "B": {"model": f"{MODEL_B[0]}:{MODEL_B[1]}", "text": ask(p["prompt"], *MODEL_B)}}
    json.dump(data, open("responses.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("Saved responses.json")
