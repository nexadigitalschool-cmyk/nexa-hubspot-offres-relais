"""Test d'intégration : run complet sur données synthétiques (hors ligne)."""
from __future__ import annotations

from pathlib import Path

from ie_prospection.config import load_config
from ie_prospection.logging_utils import setup_logging
from ie_prospection.pipeline import run


def test_end_to_end_fixture(tmp_path):
    setup_logging(tmp_path / "reports", "test")
    config = load_config(Path(__file__).resolve().parents[1] / "config" / "campuses.yml")
    paths = {
        "raw": tmp_path / "raw",
        "intermediate": tmp_path / "intermediate",
        "output": tmp_path / "output",
        "reports": tmp_path / "reports",
    }
    res = run(config, "fixture", paths, "test", resume=False)
    stats = res["stats"]

    # Volumétrie cohérente : extrait = conservé + rejeté.
    assert stats["total_extrait"] == stats["conserves"] + stats["rejetes"]
    assert stats["conserves"] > 100  # pagination réelle au-delà de 100 lignes

    # Tous les fichiers attendus existent.
    assert (tmp_path / "output" / "socle_national.csv").exists()
    assert (tmp_path / "output" / "rejected.csv").exists()
    assert (tmp_path / "output" / "campus_paris.csv").exists()
    assert (tmp_path / "reports" / "echantillon_30.csv").exists()
    assert (tmp_path / "reports" / "sources.csv").exists()
    assert (tmp_path / "reports" / "data_quality_report.md").exists()
    assert (tmp_path / "intermediate" / "annuaire_records.jsonl").exists()

    # Le fichier des rejets a un motif pour chaque ligne.
    import csv
    with (tmp_path / "output" / "rejected.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows and all(r["reject_reason"] for r in rows)

    # Cas limites présents dans les rejets.
    reasons = {r["reject_reason"] for r in rows}
    assert {"uai_absent", "uai_invalide", "doublon_uai",
            "type_hors_perimetre", "etablissement_ferme",
            "hors_perimetre_etranger"} <= reasons
