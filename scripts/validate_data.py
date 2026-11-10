#!/usr/bin/env python3
"""Validate the simulator's versioned JSON data without changing it."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    with (ROOT / "data" / name).open(encoding="utf-8") as stream:
        return json.load(stream)

def validate():
    candidates = read("candidates.json")["candidates"]
    polls = read("polls.json")
    scenarios = read("scenarios.json")
    ids = [candidate["id"] for candidate in candidates]
    names = [candidate["name"].casefold() for candidate in candidates]
    assert len(ids) == len(set(ids)), "Identifiants candidats dupliqués"
    assert len(names) == len(set(names)), "Noms candidats dupliqués"
    allowed = {"declared", "envisaged", "withdrawn", "ineligible", "official"}
    assert all(c.get("status") in allowed for c in candidates), "Statut candidat invalide"
    configurations = polls["configurations"]
    config_ids = [config["id"] for config in configurations]
    assert len(config_ids) == len(set(config_ids)), "Configurations dupliquées"
    assert polls["defaultConfiguration"] in config_ids, "Configuration par défaut absente"
    for config in configurations:
        candidate_ids = config["candidateIds"]
        values = config["values"]
        assert len(candidate_ids) == len(set(candidate_ids)), f"Candidats dupliqués dans {config['id']}"
        assert set(candidate_ids) <= set(ids), f"Candidat inconnu dans {config['id']}"
        assert set(values) == set(candidate_ids), f"Les scores doivent couvrir uniquement la configuration {config['id']}"
        assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in values.values()), f"Score invalide dans {config['id']}"
    defaults = scenarios["defaults"]
    assert all(candidate_id in ids for candidate_id in defaults["candidateIds"]), "Candidat de référence inconnu"
    assert len(scenarios["extraCandidates"]) == len({name.casefold() for name in scenarios["extraCandidates"]}), "Personnalités proposées en double"
    assert set(scenarios["transferDefaults"]) <= set(ids), "Report par défaut lié à un candidat inconnu"
    for candidate_id, shares in scenarios["transferDefaults"].items():
        assert candidate_id in ids and len(shares) == 2, "Report par défaut invalide"
        assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in shares) and sum(shares) <= 100, "Report supérieur à 100 %"
    for candidate_id, shares in defaults["transfers"].items():
        assert candidate_id in defaults["candidateIds"] and len(shares) == 2, "Report de scénario invalide"
        assert all(isinstance(v, (int, float)) and 0 <= v <= 100 for v in shares) and sum(shares) <= 100, "Report supérieur à 100 %"
    print(f"Données valides : {len(candidates)} candidats, {len(configurations)} configuration(s).")

if __name__ == "__main__":
    validate()
