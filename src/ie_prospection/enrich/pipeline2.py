"""Étape 2 — orchestration de l'enrichissement public du socle Paris (< 60 km).

Usage :
    python -m ie_prospection.enrich.pipeline2 --source fixture
    python -m ie_prospection.enrich.pipeline2 --source api

N'importe rien dans HubSpot, n'utilise aucune donnée interne, ne génère aucun
contact nominatif et ne lance aucun scoring.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from ..config import load_config
from ..logging_utils import get_logger, setup_logging
from ..schema import OUTPUT_COLUMNS
from .build import build_enriched
from .fetchers import DERIVERS, fetch_ods_source, fetch_websites
from .fixtures2 import build_fixture_results
from .schema2 import ENRICH_COLUMNS, SOURCE_SPECS, source_by_key
from .xlsx import write_xlsx

FULL_COLUMNS = OUTPUT_COLUMNS + ENRICH_COLUMNS
ANOMALY_COLUMNS = ["UAI", "Nom", "type_anomalie", "source", "detail", "date"]

INPUT_CANDIDATES = [
    "data/output/paris/01_socle_paris.csv",
    "data/output/campus_paris.csv",
]


def load_socle_paris(input_path: str | None) -> tuple[list[dict], str]:
    candidates = [input_path] if input_path else INPUT_CANDIDATES
    for cand in candidates:
        if cand and Path(cand).exists():
            with open(cand, encoding="utf-8") as f:
                return list(csv.DictReader(f)), cand
    raise FileNotFoundError(
        "Socle Paris introuvable. Lancer d'abord l'étape 1 "
        "(data/output/campus_paris.csv). Cherché : " + ", ".join(c for c in candidates if c))


def filter_within_radius(rows: list[dict], radius: float, main_academies: set[str]):
    """Ne conserve QUE les établissements à < radius km. Les lignes à distance
    inconnue sont exclues (on ne peut l'affirmer) mais journalisées."""
    kept, excluded = [], []
    for r in rows:
        d = (r.get("Distance campus km") or "").strip()
        if d:
            if float(d) <= radius:
                kept.append(r)
            else:
                excluded.append((r, f"{d} km > {radius:.0f} km"))
        else:
            excluded.append((r, "distance inconnue (GPS établissement absent)"))
    return kept, excluded


def run_sources(source: str, socle_rows, config, raw_dir, log):
    uais = [r["UAI"] for r in socle_rows if r.get("UAI")]
    if source == "fixture":
        return build_fixture_results(socle_rows)

    # source == api : best-effort, dégradation propre par source.
    results = []
    for spec in SOURCE_SPECS:
        try:
            if spec.key == "sites":
                results.append(fetch_websites(spec, socle_rows))
            else:
                results.append(fetch_ods_source(spec, uais, config.http, raw_dir,
                                                DERIVERS[spec.key]))
        except Exception as exc:  # noqa: BLE001
            from .fetchers import FetchResult, _today
            log.warning("Source « %s » en échec : %s", spec.label, exc)
            results.append(FetchResult(spec.key, spec.label, False, {},
                                       spec.dataset_ref, _today(), error=str(exc)[:300]))
    return results


def write_jointures_report(path, meta, join_stats, completeness, n_excluded):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    L = []
    L.append("# Étape 2 — Rapport de jointures & complétude (Paris)")
    L.append("")
    L.append(f"- **Run** : `{meta['run_id']}`  ·  **Date** : {meta['date']}")
    L.append(f"- **Source d'enrichissement** : {meta['source']}")
    L.append(f"- **Socle d'entrée** : `{meta['input']}` "
             f"({meta['input_total']} lignes)")
    L.append(f"- **Périmètre retenu (< {meta['radius']:.0f} km)** : "
             f"**{meta['perimeter']}** établissements "
             f"(exclus hors rayon / distance inconnue : {n_excluded})")
    L.append("")
    L.append("> Jointures réalisées **exclusivement sur l'UAI**. Aucune jointure "
             "sur le nom. Les valeurs manquantes restent vides et sont comptées.")
    L.append("")
    L.append("## Taux de jointure par source")
    L.append("")
    L.append("| Source | Dataset / réf. | Disponible | UAI joints | Taux jointure |")
    L.append("| --- | --- | :---: | ---: | ---: |")
    for s in join_stats:
        dispo = "oui" if s["available"] else "**non**"
        L.append(f"| {s['source']} | `{s['dataset_ref']}` | {dispo} | "
                 f"{s['matched']}/{s['socle_total']} | {100*s['join_rate']:.1f}% |")
    L.append("")
    # Sources indisponibles + erreurs documentées.
    ko = [s for s in join_stats if not s["available"]]
    if ko:
        L.append("### Sources indisponibles (poursuite avec valeurs vides)")
        L.append("")
        for s in ko:
            L.append(f"- **{s['source']}** : {s['error']}")
        L.append("")
    L.append("## Complétude par variable (sur le périmètre retenu)")
    L.append("")
    L.append("| Variable | Renseignées | Total | Taux |")
    L.append("| --- | ---: | ---: | ---: |")
    for col, info in completeness.items():
        L.append(f"| {col} | {info['non_empty']} | {info['total']} | "
                 f"{100*info['rate']:.1f}% |")
    L.append("")
    L.append("## Note de fiabilité")
    L.append("")
    L.append("- Les identifiants de datasets et noms de champs sont **validés au "
             "premier run en ligne** ; tout écart est journalisé. Aucun endpoint "
             "n'est inventé.")
    L.append("- Aucune donnée nominative, aucun email déduit, aucun scoring "
             "dans cette étape.")
    path.write_text("\n".join(L), encoding="utf-8")
    return path


def write_csv(path, rows, columns):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return path


def run(source: str, input_path: str | None, config_path: str, out_dir: str,
        reports_dir: str, radius: float, run_id: str) -> dict:
    log = get_logger()
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    config = load_config(config_path)

    socle_rows, used_input = load_socle_paris(input_path)
    log.info("Étape 2 — socle d'entrée : %s (%d lignes)", used_input, len(socle_rows))

    paris = config.campus_by_name("Paris")
    main_acas = set(paris.academies) if paris else set()
    radius = radius or (paris.radius_km if paris else 60.0)

    kept, excluded = filter_within_radius(socle_rows, radius, main_acas)
    log.info("Périmètre < %.0f km : %d retenus, %d exclus", radius, len(kept), len(excluded))

    out_dir = Path(out_dir)
    reports_dir = Path(reports_dir)
    raw_dir = Path("data/raw/enrich")

    # Copie de référence du socle d'entrée dans le dossier campus.
    write_csv(out_dir / "01_socle_paris.csv", socle_rows, list(socle_rows[0].keys())
              if socle_rows else OUTPUT_COLUMNS)

    results = run_sources(source, kept, config, raw_dir, log)
    for r in results:
        log.info("Source %-45s : %s (joints=%d)%s", r.label,
                 "OK" if r.available else "INDISPONIBLE", r.matched,
                 f" — {r.error}" if r.error else "")

    built = build_enriched(kept, results)
    enriched = built["enriched"]

    # Anomalies : y compris les exclusions de périmètre (non silencieuses).
    anomalies = built["anomalies"]
    for row, reason in excluded:
        anomalies.insert(0, {"UAI": row.get("UAI", ""), "Nom": row.get("Nom", ""),
                             "type_anomalie": "exclu_perimetre_60km",
                             "source": "socle étape 1", "detail": reason,
                             "date": row.get("Date extraction", "")})

    # Écritures.
    csv_path = write_csv(out_dir / "02_enrichissement_public_paris.csv",
                         enriched, FULL_COLUMNS)
    xlsx_path = write_xlsx(out_dir / "02_enrichissement_public_paris.xlsx",
                           enriched, FULL_COLUMNS, sheet_name="Enrichissement")
    anom_path = write_csv(reports_dir / "02_anomalies.csv", anomalies, ANOMALY_COLUMNS)
    ctrl_path = write_xlsx(reports_dir / "02_controle_30_lignes.xlsx",
                           enriched[:30], FULL_COLUMNS, sheet_name="Controle 30")
    meta = {"run_id": run_id, "date": date, "source": _source_label(source, results),
            "input": used_input, "input_total": len(socle_rows),
            "radius": radius, "perimeter": len(kept)}
    joint_path = write_jointures_report(reports_dir / "02_jointures.md", meta,
                                        built["join_stats"], built["completeness"],
                                        len(excluded))

    log.info("=" * 60)
    log.info("Étape 2 terminée : enrichis=%d | anomalies=%d", len(enriched), len(anomalies))
    log.info("Fichiers : %s | %s | %s | %s | %s", csv_path, xlsx_path,
             joint_path, anom_path, ctrl_path)
    return {"perimeter": len(kept), "excluded": len(excluded),
            "enriched": len(enriched), "anomalies": len(anomalies),
            "join_stats": built["join_stats"], "completeness": built["completeness"],
            "files": {"csv": str(csv_path), "xlsx": str(xlsx_path),
                      "jointures": str(joint_path), "anomalies": str(anom_path),
                      "controle": str(ctrl_path)}}


def _source_label(source, results):
    if source == "fixture":
        return "FIXTURE (données synthétiques — non officielles)"
    avail = sum(1 for r in results if r.available)
    return f"Sources publiques externes (API) — {avail}/{len(results)} disponibles"


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="NEXA — étape 2 enrichissement public (Paris)")
    p.add_argument("--source", choices=["api", "fixture"], default="api")
    p.add_argument("--input", default=None, help="Socle Paris (CSV) d'entrée")
    p.add_argument("--config", default="config/campuses.yml")
    p.add_argument("--out-dir", default="data/output/paris")
    p.add_argument("--reports-dir", default="reports/paris")
    p.add_argument("--radius-km", type=float, default=0.0,
                   help="Rayon (défaut : radius_km du campus Paris)")
    p.add_argument("--run-id", default=None)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    setup_logging(args.reports_dir, f"02_{run_id}")
    run(args.source, args.input, args.config, args.out_dir, args.reports_dir,
        args.radius_km, run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
