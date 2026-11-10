#!/usr/bin/env python3
"""Refresh every saved configuration from exact matching first-round polls."""
import json
import math
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = "https://raw.githubusercontent.com/MieuxVoter/presidentielle2027/refs/heads/main/presidentielle2027.json"

def main():
    path = ROOT / "data/polls.json"
    local = json.loads(path.read_text(encoding="utf-8"))
    with urllib.request.urlopen(urllib.request.Request(FEED, headers={"User-Agent":"Presidentielle2027-Simulator/4.0"}), timeout=45) as response:
        upstream = json.load(response)
    hypotheses = {item["id"]: frozenset(item.get("candidates", [])) for item in upstream.get("hypotheses", [])}
    polls = upstream.get("polls", [])
    if not hypotheses or not polls:
        raise ValueError("Flux amont incomplet (hypothèses ou sondages absents) : aucune donnée locale écrasée.")
    cutoff = date.today() - timedelta(days=180)
    changed = False
    for config in local["configurations"]:
        ids = config["candidateIds"]
        names = config.get("candidateNames")
        if not names:
            catalog = json.loads((ROOT / "data/candidates.json").read_text(encoding="utf-8"))["candidates"]
            by_id = {item["id"]: item["name"] for item in catalog}
            names = {cid: by_id[cid] for cid in ids}
        wanted_names = frozenset(names[cid] for cid in ids)
        grouped = {}
        for poll in polls:
            if poll.get("tour") != "1er Tour":
                continue
            hypothesis_id = poll.get("hypothese")
            hypothesis = hypotheses.get(hypothesis_id)
            if hypothesis != wanted_names:
                continue
            try:
                end = date.fromisoformat(poll["fin_enquete"])
                sample = float(poll["echantillon"])
            except (KeyError, TypeError, ValueError):
                continue
            if end < cutoff or sample <= 0:
                continue
            rows = poll.get("candidats", [])
            values = {row.get("candidat"): float(row["intentions"]) for row in rows if row.get("intentions") is not None}
            if set(values) != wanted_names or any(not math.isfinite(v) or not 0 <= v <= 100 for v in values.values()):
                continue
            grouped.setdefault(hypothesis_id, []).append((poll, values, end, sample))
        observations = [entry for entries in grouped.values() for entry in entries]
        if not observations:
            continue
        latest = max(entry[2] for entry in observations)
        weights = [math.exp(-math.log(2) * (latest-entry[2]).days/30) * math.sqrt(entry[3]/1000) for entry in observations]
        total = sum(weights)
        averages = {name: sum(w*entry[1][name] for w,entry in zip(weights, observations))/total for name in wanted_names}
        new_values = {cid: round(averages[names[cid]], 1) for cid in ids}
        institute_count = len({entry[0].get("institut") for entry in observations})
        if (new_values != config["values"] or latest.isoformat() != config.get("fieldEnd")
                or len(observations) != config.get("pollCount")
                or institute_count != config.get("pollingInstitutes")
                or config.get("sourceUrl") != "https://github.com/MieuxVoter/presidentielle2027"):
            config["values"] = new_values
            config["sourceDate"] = latest.isoformat()
            config["fieldEnd"] = latest.isoformat()
            config["pollCount"] = len(observations)
            config["pollingInstitutes"] = institute_count
            config["sourceLabel"] = "Mieux Voter — moyenne pondérée, configuration exacte"
            config["sourceUrl"] = "https://github.com/MieuxVoter/presidentielle2027"
            changed = True
    if changed:
        local["updatedAt"] = date.today().isoformat()
        path.write_text(json.dumps(local, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Instantanés des configurations correspondantes mis à jour.")
    else:
        print("Aucune enquête récente de configuration exacte; instantanés conservés.")

if __name__ == "__main__":
    main()
