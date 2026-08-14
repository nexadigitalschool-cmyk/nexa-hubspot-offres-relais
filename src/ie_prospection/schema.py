"""Schéma du socle national et cartographie des champs source.

Ce module définit :

* ``OUTPUT_COLUMNS`` : le schéma minimal de sortie (ordre stable).
* ``FIELD_MAP`` : pour chaque colonne canonique, la liste ORDONNÉE des noms
  de champ candidats côté source. On ne se fie pas à un unique nom : l'API
  de l'Annuaire de l'éducation a déjà changé de nommage par le passé, et
  les portails Opendatasoft miroirs exposent parfois des variantes. Le
  premier candidat présent (valeur non vide) est retenu ; si aucun n'est
  présent, la valeur reste vide et l'écart est journalisé (exigence :
  « détecter les champs dont le nom ou le format a changé »).

Aucune valeur d'origine n'est modifiée ici : les identifiants (UAI, SIREN,
SIRET, code postal) sont conservés en TEXTE. Seul le téléphone est normalisé,
dans une colonne séparée, sans écraser la valeur d'origine.
"""
from __future__ import annotations

# --- Schéma minimal du socle (ordre de colonnes stable et documenté) ---------
OUTPUT_COLUMNS = [
    "UAI",
    "Nom",
    "Type",
    "Statut public/privé",
    "Adresse",
    "CP",
    "Commune",
    "Académie",
    "Département",
    "Région",
    "Téléphone",
    "Mail ce.",
    "Site web",
    "SIREN",
    "SIRET",
    "Latitude",
    "Longitude",
    "Campus rattaché",
    "Distance campus km",
    "Source",
    "Date extraction",
]

# --- Cartographie colonne canonique -> candidats de champ source -------------
# Chaque liste est essayée dans l'ordre. Les noms couvrent les variantes
# connues de l'API Explore v2.1 du dataset fr-en-annuaire-education.
FIELD_MAP: dict[str, list[str]] = {
    "UAI": ["identifiant_de_l_etablissement", "numero_uai", "uai"],
    "Nom": ["nom_etablissement", "appellation_officielle", "denomination_principale"],
    "Type": ["type_etablissement"],
    "Statut public/privé": ["statut_public_prive"],
    # L'adresse est recomposée à partir des lignes adresse_1..3 (voir transform).
    "CP": ["code_postal"],
    "Commune": ["nom_commune", "libelle_commune"],
    "Académie": ["libelle_academie", "nom_academie", "academie"],
    "Département": ["libelle_departement", "nom_departement", "departement"],
    "Région": ["libelle_region", "nom_region", "region"],
    "Téléphone": ["telephone"],
    "Mail ce.": ["mail", "mel", "courriel"],
    "Site web": ["web", "site_web", "url"],
    "SIREN": ["siren", "siren_siret"],
    "SIRET": ["siret", "siren_siret"],
    "Latitude": ["latitude"],
    "Longitude": ["longitude"],
}

# Champs source additionnels utilisés pour le filtrage / la qualité,
# sans être des colonnes de sortie directes.
AUX_FIELDS: dict[str, list[str]] = {
    "libelle_nature": ["libelle_nature", "nature_uai_libe", "denomination_principale"],
    "nature_uai": ["nature_uai", "code_nature"],
    "code_departement": ["code_departement"],
    "code_academie": ["code_academie"],
    "etat": ["etat", "etat_etablissement"],
    "ministere_tutelle": ["ministere_tutelle"],
    "adresse_1": ["adresse_1", "adresse_uai"],
    "adresse_2": ["adresse_2"],
    "adresse_3": ["adresse_3"],
    "position": ["position", "geo_point_2d", "geolocalisation"],
    "code_commune": ["code_commune", "code_insee"],
}

# Colonnes du fichier de rejets.
REJECT_COLUMNS = [
    "UAI",
    "Nom",
    "Type",
    "Académie",
    "Département",
    "reject_reason",
    "reject_detail",
    "Source",
    "Date extraction",
]


def first_present(record: dict, candidates: list[str]) -> tuple[str | None, object]:
    """Retourne ``(nom_du_champ, valeur)`` pour le premier candidat présent
    avec une valeur non vide. ``(None, None)`` si aucun candidat n'est présent
    ou renseigné.
    """
    for name in candidates:
        if name in record:
            value = record[name]
            if value is not None and str(value).strip() != "":
                return name, value
    return None, None
