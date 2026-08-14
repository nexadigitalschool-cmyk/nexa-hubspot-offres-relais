"""Générateur de données de démonstration hors-ligne.

⚠️  Ces enregistrements sont SYNTHÉTIQUES. Ils reproduisent la FORME de l'API
Explore v2.1 du dataset ``fr-en-annuaire-education`` (noms de champs réels)
afin de pouvoir :
  * exécuter le pipeline de bout en bout sans accès réseau,
  * alimenter les tests (pagination, doublons, zéros initiaux, champs manquants),
  * produire des exemples de sortie.

Ils ne contiennent AUCUNE donnée nominative et ne doivent pas être confondus
avec des données officielles. Le champ ``Source`` des sorties générées à partir
de ces données porte la mention ``FIXTURE`` pour éviter toute ambiguïté.
"""
from __future__ import annotations

ACADEMIES = ["Paris", "Créteil", "Versailles"]

_DEPTS = {
    "Paris": ("075", "Paris"),
    "Créteil": ("094", "Val-de-Marne"),
    "Versailles": ("078", "Yvelines"),
}


def _record(seq: int, academie: str, nature: str, **overrides) -> dict:
    dep_code, dep_lib = _DEPTS[academie]
    letter = "ABCDEFGHJKLMNPRSTUVWXYZ"[seq % 23]
    # UAI = 7 chiffres + 1 lettre (dep_code sur 3 + 4 chiffres + lettre).
    uai = f"{dep_code}{seq % 10000:04d}{letter}"
    rec = {
        "identifiant_de_l_etablissement": uai,
        "nom_etablissement": f"Lycée démonstration {seq}",
        "type_etablissement": "Lycée",
        "libelle_nature": nature,
        "statut_public_prive": "Public" if seq % 4 else "Privé",
        "adresse_1": f"{seq} rue de l'Exemple",
        "adresse_2": "",
        "adresse_3": "",
        "code_postal": f"{dep_code}00"[:5].ljust(5, "0"),
        "code_commune": f"{dep_code}056",
        "nom_commune": f"Commune {academie} {seq % 20}",
        "libelle_academie": academie,
        "code_academie": "01",
        "libelle_departement": dep_lib,
        "code_departement": dep_code,
        "libelle_region": "Île-de-France",
        "telephone": f"01{seq % 100000000:08d}"[:10],
        "mail": f"ce.0{dep_code}{seq:04d}@ac-exemple.fr",
        "web": "",
        "siren": f"1{seq % 100000000:08d}",
        "siret": f"1{seq % 100000000:08d}{seq % 100000:05d}",
        "latitude": round(48.8 + (seq % 50) / 100, 6),
        "longitude": round(2.3 + (seq % 50) / 100, 6),
        "etat": "OUVERT",
        "ministere_tutelle": "MENJ",
    }
    rec.update(overrides)
    return rec


def build_fixture_records(n_per_academie: int = 45) -> list[dict]:
    """Construit un jeu synthétique couvrant les cas limites."""
    natures = [
        "LYCEE D ENSEIGNEMENT GENERAL ET TECHNOLOGIQUE",
        "LYCEE PROFESSIONNEL",
        "LYCEE POLYVALENT",
        "LYCEE D ENSEIGNEMENT GENERAL",
    ]
    records: list[dict] = []
    seq = 0
    for academie in ACADEMIES:
        for i in range(n_per_academie):
            seq += 1
            nature = natures[i % len(natures)]
            records.append(_record(seq, academie, nature))

    # --- Cas limites explicites (pour la qualité et les tests) ---------------
    seq += 1
    records.append(_record(seq, "Paris", "COLLEGE",
                           type_etablissement="Collège",
                           nom_etablissement="Collège hors périmètre"))
    seq += 1
    records.append(_record(seq, "Paris", "ECOLE MATERNELLE",
                           type_etablissement="Ecole",
                           nom_etablissement="Ecole hors périmètre"))
    seq += 1
    # Établissement fermé.
    records.append(_record(seq, "Créteil",
                           "LYCEE PROFESSIONNEL", etat="FERME",
                           nom_etablissement="Lycée fermé"))
    seq += 1
    # Étranger / AEFE : rattaché à une académie du périmètre (donc extrait)
    # mais code département hors France => rejeté par le garde-fou transform.
    records.append(_record(seq, "Versailles", "LYCEE POLYVALENT",
                           code_departement="099",
                           nom_etablissement="Lycee AEFE hors perimetre"))
    # UAI absent.
    rec = _record(seq + 1, "Paris", "LYCEE POLYVALENT")
    rec["identifiant_de_l_etablissement"] = ""
    records.append(rec)
    # UAI invalide.
    rec = _record(seq + 2, "Paris", "LYCEE POLYVALENT")
    rec["identifiant_de_l_etablissement"] = "ABC123"
    records.append(rec)
    # Doublon d'UAI (réutilise le 1er UAI valide).
    dup = _record(seq + 3, "Créteil", "LYCEE PROFESSIONNEL")
    dup["identifiant_de_l_etablissement"] = records[0]["identifiant_de_l_etablissement"]
    dup["nom_etablissement"] = "Doublon UAI"
    records.append(dup)
    # Sans commune.
    rec = _record(seq + 4, "Versailles", "LYCEE POLYVALENT")
    rec["nom_commune"] = ""
    rec["nom_etablissement"] = "Lycée sans commune"
    records.append(rec)
    # Sans coordonnées GPS.
    rec = _record(seq + 5, "Paris", "LYCEE D ENSEIGNEMENT GENERAL ET TECHNOLOGIQUE")
    rec["latitude"] = ""
    rec["longitude"] = ""
    rec["nom_etablissement"] = "Lycée sans GPS"
    records.append(rec)
    return records
