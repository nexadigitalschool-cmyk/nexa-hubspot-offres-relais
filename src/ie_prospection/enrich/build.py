"""Jointures UAI, provenance, taux de complétude/jointure et anomalies (étape 2).

Règle absolue : jointure sur l'UAI uniquement, jamais sur le nom. Aucune donnée
n'est déduite ; les valeurs manquantes restent vides et sont comptabilisées.
"""
from __future__ import annotations

from .schema2 import ENRICH_COLUMNS, SOURCE_SPECS, source_by_key


def build_enriched(socle_rows: list[dict], results: list[dict]) -> dict:
    """Fusionne les sources dans le socle par UAI et calcule les indicateurs.

    ``results`` : liste de FetchResult. Retourne enriched, join_stats,
    anomalies, completeness.
    """
    by_key = {r.key: r for r in results}
    total = len(socle_rows)

    enriched: list[dict] = []
    for row in socle_rows:
        out = dict(row)
        for col in ENRICH_COLUMNS:
            out.setdefault(col, "")
        uai = row.get("UAI", "").strip()
        for spec in SOURCE_SPECS:
            res = by_key.get(spec.key)
            if not res or not res.available:
                continue
            data = res.by_uai.get(uai)
            if data is None:
                continue  # join miss -> colonnes laissées vides
            for col in spec.value_columns:
                out[col] = _text(data.get(col, ""))
            out[spec.src_col] = res.source_ref
            out[spec.date_col] = res.date
        enriched.append(out)

    join_stats = _join_stats(enriched, by_key, total)
    completeness = _completeness(enriched, total)
    anomalies = _anomalies(enriched, by_key)
    return {"enriched": enriched, "join_stats": join_stats,
            "completeness": completeness, "anomalies": anomalies}


def _join_stats(enriched, by_key, total) -> list[dict]:
    stats = []
    for spec in SOURCE_SPECS:
        res = by_key.get(spec.key)
        available = bool(res and res.available)
        matched = res.matched if res else 0
        error = (res.error if res else "source non exécutée")
        cols = {}
        for col in spec.value_columns:
            non_empty = sum(1 for r in enriched if _text(r.get(col)) != "")
            cols[col] = non_empty
        stats.append({
            "source": spec.label, "key": spec.key, "dataset_ref": spec.dataset_ref,
            "available": available, "error": None if available else error,
            "matched": matched, "socle_total": total,
            "join_rate": (matched / total) if total else 0.0,
            "value_columns": spec.value_columns, "completeness_by_col": cols,
        })
    return stats


def _completeness(enriched, total) -> dict:
    out = {}
    for col in ENRICH_COLUMNS:
        if col.startswith(("Source", "Date")):
            continue
        n = sum(1 for r in enriched if _text(r.get(col)) != "")
        out[col] = {"non_empty": n, "total": total,
                    "rate": (n / total) if total else 0.0}
    return out


def _anomalies(enriched, by_key) -> list[dict]:
    anomalies: list[dict] = []

    # Anomalies au niveau source (indisponibilité globale).
    for spec in SOURCE_SPECS:
        res = by_key.get(spec.key)
        if not res or not res.available:
            anomalies.append(_anom("", "", "source_indisponible", spec.label,
                                   (res.error if res else "non exécutée"), ""))

    for r in enriched:
        uai, nom = r.get("UAI", ""), r.get("Nom", "")
        if _text(r.get("Distance campus km")) == "":
            anomalies.append(_anom(uai, nom, "distance_inconnue",
                                   "socle étape 1", "GPS établissement absent",
                                   r.get("Date extraction", "")))
        if _text(r.get("État établissement")) == "Fermé":
            anomalies.append(_anom(uai, nom, "etablissement_ferme",
                                   r.get("Source état", ""),
                                   "fermé selon la source d'état", r.get("Date état", "")))
        if _src_available(by_key, "effectifs") and _text(r.get("Effectif élèves")) == "":
            anomalies.append(_anom(uai, nom, "effectif_absent",
                                   source_by_key("effectifs").label,
                                   "UAI non joint ou effectif vide", r.get("Date effectif", "")))
        if _src_available(by_key, "ips") and _text(r.get("IPS")) == "":
            anomalies.append(_anom(uai, nom, "ips_absent",
                                   source_by_key("ips").label,
                                   "UAI non joint dans l'IPS", r.get("Date IPS", "")))
        if _src_available(by_key, "onisep_formations") and \
                all(_text(r.get(c)) == "" for c in
                    ("Filière NSI", "Filière SNT", "Filière STI2D", "Filière STMG", "Bac pro SN")):
            anomalies.append(_anom(uai, nom, "filieres_indisponibles",
                                   source_by_key("onisep_formations").label,
                                   "UAI non joint dans Idéo-Formations", ""))
        if _src_available(by_key, "onisep_structures") and \
                _text(r.get("Présent ONISEP structures")) != "O":
            anomalies.append(_anom(uai, nom, "absent_onisep_structures",
                                   source_by_key("onisep_structures").label,
                                   "UAI absent d'Idéo-Structures", ""))
        if _text(r.get("Site web")) == "":
            anomalies.append(_anom(uai, nom, "site_absent", "socle",
                                   "pas d'URL de site officiel", ""))
        elif _src_available(by_key, "sites") and _text(r.get("Source site")) == "":
            anomalies.append(_anom(uai, nom, "site_non_analyse",
                                   source_by_key("sites").label,
                                   "site présent mais non analysé/injoignable", ""))
    return anomalies


def _src_available(by_key, key) -> bool:
    res = by_key.get(key)
    return bool(res and res.available)


def _anom(uai, nom, type_a, source, detail, date) -> dict:
    return {"UAI": uai, "Nom": nom, "type_anomalie": type_a,
            "source": source, "detail": detail, "date": date}


def _text(v) -> str:
    if v is None:
        return ""
    return str(v).strip()
