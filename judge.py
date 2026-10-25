"""Step 3: LLM judge compares each pair TWICE (both orders) to measure position bias.
Usage: python judge.py [provider] [model]"""
import csv, json, re, sys
from llm import ask

provider = sys.argv[1] if len(sys.argv) > 1 else None
model = sys.argv[2] if len(sys.argv) > 2 else None
guide = open("guidelines.md", encoding="utf-8").read()
prompts = {p["id"]: p for p in csv.DictReader(open("prompts.csv", encoding="utf-8"))}
data = json.load(open("responses.json", encoding="utf-8"))


def judge(prompt, r1, r2):
    q = (f"{guide}\n\nPROMPT: {prompt}\n\n----- RESPONSE 1 -----\n{r1}\n\n----- RESPONSE 2 -----\n{r2}\n\n"
         'Reply ONLY with JSON: {"winner": "1" or "2" or "tie", "reason": "one sentence"}')
    raw = ask(q, provider, model)
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"winner": "error", "reason": raw[:150]}


with open("judge_prefs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "winner_AB_order", "winner_BA_order", "consistent", "reason"])
    for pid, pair in data.items():
        p = prompts[pid]["prompt"]
        j1 = judge(p, pair["A"]["text"], pair["B"]["text"])          # A shown first
        j2 = judge(p, pair["B"]["text"], pair["A"]["text"])          # B shown first
        w1 = {"1": "A", "2": "B"}.get(str(j1["winner"]), str(j1["winner"]))
        w2 = {"1": "B", "2": "A"}.get(str(j2["winner"]), str(j2["winner"]))
        print(f"[{pid}] AB-order: {w1}  BA-order: {w2}")
        w.writerow([pid, w1, w2, w1 == w2, j1.get("reason", "")])
print("Saved judge_prefs.csv")
