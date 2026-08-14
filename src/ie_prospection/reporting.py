"""Écriture des sorties : CSV, rapport qualité, manifeste des sources, échantillon."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from .schema import FIELD_MAP, OUTPUT_COLUMNS, REJECT_COLUMNS


def write_csv(path: str | Path, rows: list[dict], columns: list[str]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_socle(path, rows) -> Path:
    return write_csv(path, rows, OUTPUT_COLUMNS)


def write_rejects(path, rows) -> Path:
    return write_csv(path, rows, REJECT_COLUMNS)


def write_jsonl(path: str | Path, records) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return path


def write_sample(path, rows, n: int = 30) -> Path:
    return write_csv(path, rows[:n], OUTPUT_COLUMNS)


def write_sources_manifest(path: str | Path, entries: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["source", "dataset_id", "base_url", "where", "url_exemple",
               "date_extraction", "volume_extrait", "volume_conserve"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for e in entries:
            writer.writerow(e)
    # Version JSON en parallèle.
    Path(str(path).replace(".csv", ".json")).write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_quality_report(path: str | Path, stats: dict, field_presence: dict,
                         drift: list[str], per_campus: dict, meta: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Rapport de qualité — Socle national des lycées (NEXA)")
    lines.append("")
    lines.append(f"- **Run** : `{meta.get('run_id')}`")
    lines.append(f"- **Date d'extraction** : {meta.get('extraction_date')}")
    lines.append(f"- **Source** : {meta.get('source_label')}")
    lines.append(f"- **Périmètre** : {', '.join(meta.get('academies', []))}")
    lines.append("")
    lines.append("## Volumétrie")
    lines.append("")
    lines.append(f"- Enregistrements extraits : **{stats['total_extrait']}**")
    lines.append(f"- Conservés (socle) : **{stats['conserves']}**")
    lines.append(f"- Rejetés : **{stats['rejetes']}**")
    lines.append("")
    lines.append("### Rejets par motif")
    lines.append("")
    if stats["rejets_par_motif"]:
        lines.append("| Motif | Nombre |")
        lines.append("| --- | ---: |")
        for motif, n in sorted(stats["rejets_par_motif"].items(), key=lambda x: -x[1]):
            lines.append(f"| {motif} | {n} |")
    else:
        lines.append("_Aucun rejet._")
    lines.append("")
    lines.append("### Signalements (conservés mais à surveiller)")
    lines.append("")
    sig = stats.get("signalements", {})
    lines.append(f"- Sans commune : **{sig.get('sans_commune', 0)}**")
    lines.append(f"- Sans coordonnées GPS : **{sig.get('gps_absent', 0)}**")
    lines.append("")
    lines.append("## Complétude des champs (sur enregistrements extraits)")
    lines.append("")
    lines.append("| Colonne | Présence | Taux |")
    lines.append("| --- | ---: | ---: |")
    total = max(stats["total_extrait"], 1)
    for col in OUTPUT_COLUMNS:
        if col in FIELD_MAP:
            n = field_presence.get(col, 0)
            lines.append(f"| {col} | {n} | {100*n/total:.1f}% |")
    lines.append("")
    if drift:
        lines.append("## ⚠️ Champs jamais résolus (renommage/format probable)")
        lines.append("")
        for col in drift:
            lines.append(f"- **{col}** : aucun champ candidat trouvé dans la source.")
        lines.append("")
    lines.append("## Distribution nature/type rencontrée")
    lines.append("")
    lines.append("| Nature / Type | Nombre |")
    lines.append("| --- | ---: |")
    for k, n in list(stats.get("distribution_type_nature", {}).items())[:40]:
        lines.append(f"| {k} | {n} |")
    lines.append("")
    lines.append("## Répartition par campus (socle conservé)")
    lines.append("")
    lines.append("| Campus | Lignes | Distance calculée |")
    lines.append("| --- | ---: | :---: |")
    for campus, info in per_campus.items():
        dist = "oui" if info.get("distance_enabled") else "non (coordonnées campus manquantes)"
        lines.append(f"| {campus} | {info['count']} | {dist} |")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    Path(str(path).replace(".md", ".json")).write_text(
        json.dumps({"stats": stats, "field_presence": field_presence,
                    "drift": drift, "per_campus": per_campus, "meta": meta},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return path
