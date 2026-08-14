"""Tests de normalisation, filtrage, dédup, zéros initiaux, champs manquants."""
from __future__ import annotations

import logging

from ie_prospection.config import (
    AppConfig,
    Campus,
    HttpConfig,
    LyceeFilter,
    SourceConfig,
)
from ie_prospection.transform import (
    assign_campus,
    build_row,
    classify,
    normalize_phone,
    transform_records,
    validate_uai,
)

LOG = logging.getLogger("test")


def _filter():
    return LyceeFilter(
        keep_natures=[
            "LYCEE D ENSEIGNEMENT GENERAL ET TECHNOLOGIQUE",
            "LYCEE PROFESSIONNEL",
            "LYCEE POLYVALENT",
        ],
        keep_types=["Lycée"],
        exclude_types=["Ecole", "Collège"],
        exclude_foreign=True,
        only_open=True,
    )


def _config(campuses=None):
    return AppConfig(
        source=SourceConfig("fr-en-annuaire-education", "https://x/api"),
        http=HttpConfig(),
        lycee_filter=_filter(),
        campuses=campuses or [Campus(name="Paris", academies=["Paris"], active=True)],
    )


def _lycee(**over):
    rec = {
        "identifiant_de_l_etablissement": "0750001A",
        "nom_etablissement": "Lycée Test",
        "type_etablissement": "Lycée",
        "libelle_nature": "LYCEE POLYVALENT",
        "statut_public_prive": "Public",
        "adresse_1": "1 rue A",
        "code_postal": "07500",
        "nom_commune": "Paris",
        "libelle_academie": "Paris",
        "libelle_departement": "Paris",
        "code_departement": "075",
        "libelle_region": "Île-de-France",
        "telephone": "0140000000",
        "mail": "ce.0750001a@ac-paris.fr",
        "siren": "005410099",
        "siret": "00541009900012",
        "latitude": 48.85,
        "longitude": 2.35,
        "etat": "OUVERT",
    }
    rec.update(over)
    return rec


# --- Normalisation téléphone -------------------------------------------------
def test_normalize_phone_variants():
    assert normalize_phone("01 40 00 00 00") == "+33140000000"
    assert normalize_phone("+33140000000") == "+33140000000"
    assert normalize_phone("0033140000000") == "+33140000000"
    assert normalize_phone("") == ""
    assert normalize_phone(None) == ""


# --- Validation UAI ----------------------------------------------------------
def test_validate_uai():
    assert validate_uai("0750001A")
    assert not validate_uai("ABC123")
    assert not validate_uai("075001A")   # 6 chiffres
    assert not validate_uai("")


# --- Zéros initiaux préservés (texte) ---------------------------------------
def test_leading_zeros_preserved():
    row = build_row(_lycee(), "src", "2026-01-01")
    assert row["UAI"] == "0750001A"
    assert row["CP"] == "07500"
    assert row["SIREN"] == "005410099"
    assert row["SIRET"] == "00541009900012"
    # Restent des chaînes, pas des entiers.
    for col in ("UAI", "CP", "SIREN", "SIRET"):
        assert isinstance(row[col], str)


# --- Champs manquants restent vides -----------------------------------------
def test_missing_fields_stay_empty():
    rec = _lycee()
    rec.pop("web", None)
    rec["nom_commune"] = ""
    rec["latitude"] = ""
    rec["longitude"] = ""
    row = build_row(rec, "src", "2026-01-01")
    assert row["Commune"] == ""
    assert row["Site web"] == ""
    assert row["Latitude"] == ""
    assert row["Longitude"] == ""


# --- Classification ----------------------------------------------------------
def test_classify_keeps_lycee():
    keep, reason, _ = classify(_lycee(), _filter())
    assert keep and reason is None


def test_classify_rejects_college():
    keep, reason, _ = classify(
        _lycee(type_etablissement="Collège", libelle_nature="COLLEGE"), _filter())
    assert not keep and reason == "type_hors_perimetre"


def test_classify_rejects_foreign():
    keep, reason, _ = classify(
        _lycee(libelle_academie="Etranger", code_departement="099"), _filter())
    assert not keep and reason == "hors_perimetre_etranger"


def test_classify_rejects_closed():
    keep, reason, _ = classify(_lycee(etat="FERME"), _filter())
    assert not keep and reason == "etablissement_ferme"


# --- Déduplication UAI + comptage -------------------------------------------
def test_transform_dedup_and_counts():
    records = [
        _lycee(identifiant_de_l_etablissement="0750001A"),
        _lycee(identifiant_de_l_etablissement="0750001A", nom_etablissement="Doublon"),
        _lycee(identifiant_de_l_etablissement="0750002B"),
        _lycee(identifiant_de_l_etablissement="", nom_etablissement="Sans UAI"),
        _lycee(identifiant_de_l_etablissement="BADUAI0", nom_etablissement="UAI invalide"),
        _lycee(type_etablissement="Collège", libelle_nature="COLLEGE"),
    ]
    res = transform_records(records, _config(), "src", "2026-01-01", LOG)
    stats = res["stats"]
    assert stats["total_extrait"] == 6
    assert stats["conserves"] == 2
    motifs = stats["rejets_par_motif"]
    assert motifs.get("doublon_uai") == 1
    assert motifs.get("uai_absent") == 1
    assert motifs.get("uai_invalide") == 1
    assert motifs.get("type_hors_perimetre") == 1


def test_transform_flags_missing_commune_and_gps():
    records = [
        _lycee(identifiant_de_l_etablissement="0750010A", nom_commune=""),
        _lycee(identifiant_de_l_etablissement="0750011B", latitude="", longitude=""),
    ]
    res = transform_records(records, _config(), "src", "2026-01-01", LOG)
    sig = res["stats"]["signalements"]
    assert sig.get("sans_commune") == 1
    assert sig.get("gps_absent") == 1
    # Les deux sont CONSERVÉS (signalés, non rejetés).
    assert res["stats"]["conserves"] == 2


# --- Détection de drift (champ renommé/absent) ------------------------------
def test_drift_detection_when_field_renamed():
    # 'nom_etablissement' renommé -> 'Nom' jamais résolu.
    records = []
    for i in range(3):
        r = _lycee(identifiant_de_l_etablissement=f"075{i:04d}A")
        r["denomination"] = r.pop("nom_etablissement")  # champ inconnu
        records.append(r)
    res = transform_records(records, _config(), "src", "2026-01-01", LOG)
    assert "Nom" in res["drift"]


# --- Affectation campus + distance ------------------------------------------
def test_campus_assignment_no_coords_disables_distance():
    campus = Campus(name="Paris", academies=["Paris"], active=True,
                    latitude=None, longitude=None)
    row = build_row(_lycee(), "src", "2026-01-01")
    assign_campus(row, [campus])
    assert row["Campus rattaché"] == "Paris"
    assert row["Distance campus km"] == ""   # désactivé faute de coordonnées


def test_campus_assignment_with_coords_computes_distance():
    campus = Campus(name="Paris", academies=["Paris"], active=True,
                    latitude=48.86, longitude=2.34)
    row = build_row(_lycee(), "src", "2026-01-01")
    assign_campus(row, [campus])
    assert row["Campus rattaché"] == "Paris"
    assert row["Distance campus km"] != ""
    assert float(row["Distance campus km"]) < 5  # même quartier


def test_priority_department_wins():
    bordeaux = Campus(name="Bordeaux", academies=["Bordeaux"],
                      priority_departments=["033"], active=True)
    row = build_row(_lycee(libelle_academie="Bordeaux", code_departement="033",
                           libelle_departement="Gironde"), "src", "2026-01-01")
    assign_campus(row, [bordeaux])
    assert row["Campus rattaché"] == "Bordeaux"


# --- Règle des 60 km / départements tampons ---------------------------------
def _paris_campus():
    return Campus(name="Paris", academies=["Paris", "Créteil", "Versailles"],
                  priority_departments=["075", "077", "078", "091", "092", "093",
                                        "094", "095"],
                  buffer_departments=["027", "028", "045", "060"],
                  radius_km=60, latitude=48.8710, longitude=2.3652, active=True)


def _config_paris():
    return AppConfig(
        source=SourceConfig("fr-en-annuaire-education", "https://x/api"),
        http=HttpConfig(), lycee_filter=_filter(), campuses=[_paris_campus()])


def test_seine_et_marne_fully_included():
    # 77 (Créteil) : conservé sans condition de distance, même éloigné.
    rec = _lycee(identifiant_de_l_etablissement="0771234A", libelle_academie="Créteil",
                 code_departement="077", latitude=48.55, longitude=3.05)  # ~55 km
    res = transform_records([rec], _config_paris(), "src", "2026-01-01", LOG)
    assert res["stats"]["conserves"] == 1


def test_buffer_within_radius_kept():
    rec = _lycee(identifiant_de_l_etablissement="0601234B", libelle_academie="Amiens",
                 code_departement="060", latitude=49.19, longitude=2.47)  # ~36 km
    res = transform_records([rec], _config_paris(), "src", "2026-01-01", LOG)
    assert res["stats"]["conserves"] == 1
    assert res["stats"]["signalements"].get("tampons_conserves") == 1


def test_buffer_beyond_radius_rejected():
    rec = _lycee(identifiant_de_l_etablissement="0451234C", libelle_academie="Orléans-Tours",
                 code_departement="045", latitude=47.90, longitude=1.90)  # ~108 km
    res = transform_records([rec], _config_paris(), "src", "2026-01-01", LOG)
    assert res["stats"]["conserves"] == 0
    assert res["stats"]["rejets_par_motif"].get("hors_rayon_km") == 1


def test_buffer_without_gps_not_verifiable():
    rec = _lycee(identifiant_de_l_etablissement="0601235D", libelle_academie="Amiens",
                 code_departement="060", latitude="", longitude="")
    res = transform_records([rec], _config_paris(), "src", "2026-01-01", LOG)
    assert res["stats"]["conserves"] == 0
    assert res["stats"]["rejets_par_motif"].get("distance_non_verifiable") == 1


def test_main_academie_kept_regardless_of_distance():
    # Versailles éloigné (Rambouillet-like) : académie principale -> conservé.
    rec = _lycee(identifiant_de_l_etablissement="0781234E", libelle_academie="Versailles",
                 code_departement="078", latitude=48.55, longitude=1.75)
    res = transform_records([rec], _config_paris(), "src", "2026-01-01", LOG)
    assert res["stats"]["conserves"] == 1
