"""Step 2 (YOUR work): blind side-by-side comparison following guidelines.md
Usage: python compare.py      (resumes; q to quit)"""
import csv, json, os, random

DIMS = ["correctness", "helpfulness", "clarity", "language_fit"]
prompts = {p["id"]: p for p in csv.DictReader(open("prompts.csv", encoding="utf-8"))}
data = json.load(open("responses.json", encoding="utf-8"))
done = set()
if os.path.exists("human_prefs.csv"):
    done = {r["id"] for r in csv.DictReader(open("human_prefs.csv", encoding="utf-8"))}
new = not os.path.exists("human_prefs.csv")
cols = ["id", "shown_first"] + [f"{s}_{d}" for s in ("A", "B") for d in DIMS] + ["winner", "reason"]


def score(label):
    while True:
        v = input(f"    {label} (1-5): ").strip()
        if v in {"1", "2", "3", "4", "5"}:
            return int(v)


with open("human_prefs.csv", "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    if new:
        w.writeheader()
    for pid, pair in data.items():
        if pid in done:
            continue
        first = random.choice(["A", "B"])           # blind + random order
        order = [first, "B" if first == "A" else "A"]
        print("\n" + "=" * 75 + f"\n{pid} | {prompts[pid]['category']} | {prompts[pid]['language']}")
        print(f"PROMPT: {prompts[pid]['prompt']}")
        for i, key in enumerate(order, 1):
            print(f"\n----- RESPONSE {i} -----\n{pair[key]['text']}")
        if input("\nPress Enter to score (q to quit): ").strip() == "q":
            break
        row = {"id": pid, "shown_first": first}
        for i, key in enumerate(order, 1):
            print(f"  Response {i}:")
            for d in DIMS:
                row[f"{key}_{d}"] = score(d)
        pick = ""
        while pick not in {"1", "2", "tie"}:
            pick = input("Overall winner (1 / 2 / tie): ").strip().lower()
        row["winner"] = "tie" if pick == "tie" else order[int(pick) - 1]
        row["reason"] = input("Why (one sentence): ").strip()
        w.writerow(row)
        f.flush()
print("Saved human_prefs.csv")
