"""Tests étape 2 : jointures UAI, périmètre 60 km, complétude, indisponibilité."""
from __future__ import annotations

from ie_prospection.enrich.build import build_enriched
from ie_prospection.enrich.fetchers import FetchResult, fetch_websites
from ie_prospection.enrich.schema2 import source_by_key
from ie_prospection.enrich.pipeline2 import (
    FULL_COLUMNS,
    filter_within_radius,
    read_socle_csv,
)
from ie_prospection.enrich.schema2 import ENRICH_COLUMNS


def _socle(uai, **over):
    row = {c: "" for c in ["UAI", "Nom", "Académie", "Distance campus km",
                           "Site web", "Date extraction"]}
    row["UAI"] = uai
    row["Nom"] = f"Lycée {uai}"
    row["Distance campus km"] = "10.0"
    row.update(over)
    return row


def _res(key, by_uai, available=True, error=None):
    return FetchResult(key, key, available, by_uai, "ref", "2026-01-01",
                       error=error, matched=len(by_uai))


# --- Jointure sur UAI --------------------------------------------------------
def test_join_is_by_uai_only():
    socle = [_socle("0750001A"), _socle("0750002B")]
    results = [
        _res("effectifs", {"0750001A": {"Effectif élèves": "800"}}),
        _res("ips", {"0750002B": {"IPS": "110"}}),
    ]
    out = build_enriched(socle, results)
    rows = {r["UAI"]: r for r in out["enriched"]}
    assert rows["0750001A"]["Effectif élèves"] == "800"
    assert rows["0750001A"]["IPS"] == ""        # pas de jointure croisée
    assert rows["0750002B"]["IPS"] == "110"
    assert rows["0750002B"]["Effectif élèves"] == ""


def test_join_never_matches_on_name():
    # Même nom, UAI différents -> aucune contamination.
    socle = [_socle("0750001A", Nom="Lycée Charles Péguy"),
             _socle("0750002B", Nom="Lycée Charles Péguy")]
    results = [_res("effectifs", {"0750001A": {"Effectif élèves": "900"}})]
    out = build_enriched(socle, results)
    rows = {r["UAI"]: r for r in out["enriched"]}
    assert rows["0750002B"]["Effectif élèves"] == ""


# --- Provenance (source + date) ---------------------------------------------
def test_provenance_columns_filled_on_match_only():
    socle = [_socle("0750001A"), _socle("0750002B")]
    results = [_res("ips", {"0750001A": {"IPS": "115"}})]
    out = build_enriched(socle, results)
    rows = {r["UAI"]: r for r in out["enriched"]}
    assert rows["0750001A"]["Source IPS"] == "ref"
    assert rows["0750001A"]["Date IPS"] == "2026-01-01"
    assert rows["0750002B"]["Source IPS"] == ""   # non joint -> pas de provenance


# --- Taux de jointure & complétude ------------------------------------------
def test_join_rate_and_completeness():
    socle = [_socle(f"075{i:04d}A") for i in range(10)]
    matched = {r["UAI"]: {"IPS": "100"} for r in socle[:6]}
    out = build_enriched(socle, [_res("ips", matched)])
    js = {s["key"]: s for s in out["join_stats"]}
    assert js["ips"]["matched"] == 6
    assert abs(js["ips"]["join_rate"] - 0.6) < 1e-9
    assert abs(out["completeness"]["IPS"]["rate"] - 0.6) < 1e-9


# --- Source indisponible -> valeurs vides + documenté ------------------------
def test_unavailable_source_leaves_empty_and_documents():
    socle = [_socle("0750001A")]
    results = [_res("ips", {}, available=False, error="egress bloqué")]
    out = build_enriched(socle, results)
    assert out["enriched"][0]["IPS"] == ""
    js = {s["key"]: s for s in out["join_stats"]}
    assert js["ips"]["available"] is False
    assert js["ips"]["error"] == "egress bloqué"
    # Anomalie source_indisponible présente.
    assert any(a["type_anomalie"] == "source_indisponible" and "IPS" in a["source"]
               for a in out["anomalies"])


# --- Sites : un 403 (proxy/egress) n'est PAS une page exploitable -----------
class _Resp:
    def __init__(self, code, text=""):
        self.status_code = code
        self.text = text


class _Sess403:
    def get(self, url, timeout=None):
        return _Resp(403, "Access denied")


class _SessOK:
    def get(self, url, timeout=None):
        return _Resp(200, "<p>bureau des entreprises</p>")


def test_websites_403_not_counted_as_reachable():
    rows = [{"UAI": "0750001A", "Site web": "http://x.fr"}]
    res = fetch_websites(source_by_key("sites"), rows, session=_Sess403())
    assert res.available is False and res.matched == 0


def test_websites_200_detects_keywords():
    rows = [{"UAI": "0750001A", "Site web": "http://x.fr"}]
    res = fetch_websites(source_by_key("sites"), rows, session=_SessOK())
    assert res.available is True
    assert res.by_uai["0750001A"]["Bureau des entreprises"] == "O"


# --- Périmètre 60 km ---------------------------------------------------------
def test_perimeter_filter_keeps_under_radius():
    rows = [_socle("A", **{"Distance campus km": "30"}),
            _socle("B", **{"Distance campus km": "75"}),
            _socle("C", **{"Distance campus km": ""})]
    kept, excluded = filter_within_radius(rows, 60.0, {"Paris"})
    assert [r["UAI"] for r in kept] == ["A"]
    assert len(excluded) == 2   # >60 km et distance inconnue


# --- Lecture du socle réel (séparateur ';' + BOM + zéros initiaux) ----------
def test_read_socle_csv_semicolon_bom(tmp_path):
    p = tmp_path / "01_socle_paris.csv"
    p.write_text("﻿UAI;Nom;CP;Distance campus km;Téléphone normalisé\n"
                 "0930933J;Lycée Assomption;93140;9.61;+33148495174\n",
                 encoding="utf-8")
    rows, header = read_socle_csv(str(p))
    assert header[0] == "UAI"                       # BOM retiré
    assert "Téléphone normalisé" in header          # colonne réelle préservée
    assert rows[0]["UAI"] == "0930933J"             # texte, zéro initial conservé
    assert rows[0]["CP"] == "93140"
    assert rows[0]["Distance campus km"] == "9.61"


def test_read_socle_csv_comma_still_works(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("UAI,Nom,CP\n0750001A,Lycée X,75008\n", encoding="utf-8")
    rows, header = read_socle_csv(str(p))
    assert header == ["UAI", "Nom", "CP"]
    assert rows[0]["CP"] == "75008"


# --- Aucune colonne nominative ----------------------------------------------
def test_no_nominative_columns():
    forbidden = ("proviseur", "prénom", "prenom", "civilité", "nom du contact")
    for col in FULL_COLUMNS:
        assert not any(f in col.lower() for f in forbidden)
    # Aucune colonne d'enrichissement ne collecte d'email personnel.
    assert "Mail ce." in FULL_COLUMNS  # institutionnel, hérité du socle
    for c in ENRICH_COLUMNS:
        assert "mail" not in c.lower() and "email" not in c.lower()
