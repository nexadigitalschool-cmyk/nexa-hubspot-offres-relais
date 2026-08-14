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

    # --- Départements tampons (AUTRES académies) : test de la règle 60 km ----
    # Campus Paris ~ (48.8710, 2.3652). On place des points en-deçà et au-delà.
    base = seq + 6
    records += [
        # Oise (60, académie d'Amiens) ~36 km -> CONSERVÉ.
        _buffer_record(base + 0, "060", "Amiens", "Picardie", 49.19, 2.47,
                       "Lycee Oise proche (~36km)"),
        # Eure (27, académie de Normandie) ~36 km -> CONSERVÉ.
        _buffer_record(base + 1, "027", "Normandie", "Normandie", 49.05, 1.95,
                       "Lycee Eure proche (~36km)"),
        # Loiret (45, académie d'Orléans-Tours) ~108 km -> REJETÉ (hors rayon).
        _buffer_record(base + 2, "045", "Orléans-Tours", "Centre-Val de Loire",
                       47.90, 1.90, "Lycee Loiret lointain (~108km)"),
        # Eure-et-Loir (28, Orléans-Tours) ~80 km -> REJETÉ (hors rayon).
        _buffer_record(base + 3, "028", "Orléans-Tours", "Centre-Val de Loire",
                       48.44, 1.49, "Lycee Chartres (~80km)"),
        # Oise sans GPS -> REJETÉ (distance non vérifiable).
        _buffer_record(base + 4, "060", "Amiens", "Picardie", None, None,
                       "Lycee Oise sans GPS"),
    ]
    return records


def _buffer_record(seq: int, dep_code: str, academie: str, region: str,
                   lat, lon, nom: str) -> dict:
    letter = "ABCDEFGHJKLMNPRSTUVWXYZ"[seq % 23]
    uai = f"{dep_code}{seq % 10000:04d}{letter}"
    return {
        "identifiant_de_l_etablissement": uai,
        "nom_etablissement": nom,
        "type_etablissement": "Lycée",
        "libelle_nature": "LYCEE POLYVALENT",
        "statut_public_prive": "Public",
        "adresse_1": f"{seq} avenue Tampon",
        "code_postal": f"{dep_code}00"[:5].ljust(5, "0"),
        "code_commune": f"{dep_code}100",
        "nom_commune": f"Commune {dep_code}",
        "libelle_academie": academie,
        "code_academie": "99",
        "libelle_departement": f"Dept {dep_code}",
        "code_departement": dep_code,
        "libelle_region": region,
        "telephone": "0300000000",
        "mail": f"ce.{dep_code}{seq:04d}@ac-exemple.fr",
        "web": "",
        "siren": f"2{seq % 100000000:08d}",
        "siret": f"2{seq % 100000000:08d}00011",
        "latitude": "" if lat is None else lat,
        "longitude": "" if lon is None else lon,
        "etat": "OUVERT",
        "ministere_tutelle": "MENJ",
    }
