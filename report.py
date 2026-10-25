"""Step 4: win rates, judge agreement, position bias + export the preference dataset."""
import csv, json, os
import pandas as pd

prompts = pd.read_csv("prompts.csv")
data = json.load(open("responses.json", encoding="utf-8"))
h = pd.read_csv("human_prefs.csv").fillna("").merge(prompts, on="id")
name = {"A": data[h["id"].iloc[0]]["A"]["model"], "B": data[h["id"].iloc[0]]["B"]["model"]}
DIMS = ["correctness", "helpfulness", "clarity", "language_fit"]

lines = ["# Results\n", f"Pairs compared by me: {len(h)}\n", "## Human win rate\n"]
lines.append(h["winner"].map(lambda x: name.get(x, "tie")).value_counts(normalize=True).mul(100).round(0).to_markdown())
dims = pd.DataFrame({name[s]: [h[f"{s}_{d}"].mean() for d in DIMS] for s in "AB"}, index=DIMS).round(2)
lines += ["\n## Average scores (1–5)\n", dims.to_markdown()]
by_cat = h.groupby("category")["winner"].agg(lambda s: f"A {(s=='A').sum()} / B {(s=='B').sum()} / tie {(s=='tie').sum()}")
lines += ["\n## Winner by category\n", by_cat.to_markdown()]

if os.path.exists("judge_prefs.csv"):
    j = pd.read_csv("judge_prefs.csv").merge(h[["id", "winner"]], on="id")
    cons = j["consistent"].mean()
    c = j[j["consistent"]]
    agree = f"{(c['winner_AB_order'] == c['winner']).mean():.0%}" if len(c) else "n/a (no consistent pairs)"
    lines += ["\n## LLM judge\n",
              f"- Position consistency (same winner in both orders): {cons:.0%}",
              f"- Agreement with my label (on consistent pairs): {agree}",
              f"- Picked whichever was shown first when inconsistent: "
              f"{((j['winner_AB_order']=='A') & (j['winner_BA_order']=='B')).sum()} of {(~j['consistent']).sum()}"]

# export RLHF-style preference data (ties skipped)
with open("preference_dataset.jsonl", "w", encoding="utf-8") as f:
    for _, r in h[h["winner"] != "tie"].iterrows():
        lose = "B" if r["winner"] == "A" else "A"
        f.write(json.dumps({"prompt": r["prompt"], "chosen": data[r["id"]][r["winner"]]["text"],
                            "rejected": data[r["id"]][lose]["text"], "reason": r["reason"],
                            "language": r["language"]}, ensure_ascii=False) + "\n")
lines.append(f"\nExported {int((h['winner'] != 'tie').sum())} preference pairs -> preference_dataset.jsonl")
open("report.md", "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
