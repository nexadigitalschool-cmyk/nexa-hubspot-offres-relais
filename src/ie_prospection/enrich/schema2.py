"""Schéma de l'étape 2 : colonnes d'enrichissement et spécification des sources.

Chaque source publique renseigne un groupe de colonnes de valeur + un couple
(colonne Source, colonne Date) traçant sa provenance et sa date d'extraction.
Les identifiants de datasets et noms de champs sont des CANDIDATS : ils sont
résolus/validés au premier run en ligne (comme à l'étape 1) et, à défaut,
documentés comme indisponibles. On n'invente aucun endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# --- Colonnes d'enrichissement ajoutées au socle (ordre stable) --------------
ENRICH_COLUMNS = [
    # ONISEP Idéo-Formations : filières
    "Filière NSI", "Filière SNT", "Filière STI2D", "Filière STMG", "Bac pro SN",
    "Source filières", "Date filières",
    # Effectifs officiels
    "Effectif élèves",
    "Source effectif", "Date effectif",
    # IPS
    "IPS",
    "Source IPS", "Date IPS",
    # Parcoursup : présence BTS / post-bac
    "BTS ou post-bac",
    "Source post-bac", "Date post-bac",
    # Établissements fermés : état actif/fermé
    "État établissement",
    "Source état", "Date état",
    # ONISEP Idéo-Structures : présence dans l'annuaire ONISEP (validation join)
    "Présent ONISEP structures",
    "Source structures", "Date structures",
    # Sites officiels : bureau des entreprises / forum orientation
    "Bureau des entreprises", "Forum ou événement orientation",
    "Source site", "Date site",
]


@dataclass
class EnrichSource:
    """Spécification d'une source publique d'enrichissement."""
    key: str
    label: str                      # nom lisible de la source
    value_columns: list[str]        # colonnes de valeur renseignées
    src_col: str                    # colonne "Source ..."
    date_col: str                   # colonne "Date ..."
    dataset_ref: str                # id de dataset ou URL (documenté)
    base_url: str = ""              # base API si applicable
    uai_field_candidates: list[str] = field(default_factory=list)
    note: str = ""


# NB : les dataset_ref ci-dessous sont les identifiants publics connus, À
# CONFIRMER au premier run en ligne. Aucun n'est joignable depuis cet
# environnement (egress bloqué) — l'étape se poursuit alors avec des valeurs
# vides, documentées dans le rapport de jointures.
SOURCE_SPECS: list[EnrichSource] = [
    EnrichSource(
        key="onisep_formations",
        label="ONISEP Idéo-Formations",
        value_columns=["Filière NSI", "Filière SNT", "Filière STI2D",
                       "Filière STMG", "Bac pro SN"],
        src_col="Source filières", date_col="Date filières",
        dataset_ref="ideo-formations-initiales-en-france (opendata.onisep.fr)",
        base_url="https://opendata.onisep.fr",
        uai_field_candidates=["code_uai", "uai", "identifiant_de_l_etablissement"],
        note="Dérivation des filières depuis les intitulés de formations.",
    ),
    EnrichSource(
        key="effectifs",
        label="Effectifs officiels lycées (data.education.gouv.fr)",
        value_columns=["Effectif élèves"],
        src_col="Source effectif", date_col="Date effectif",
        dataset_ref="fr-en-lycee_gt-effectifs-niveau-sexe-lv + "
                    "fr-en-lycee_pro-effectifs-niveau-sexe-lv",
        base_url="https://data.education.gouv.fr/api/explore/v2.1",
        uai_field_candidates=["numero_lycee", "uai", "numero_etablissement",
                              "identifiant_de_l_etablissement"],
    ),
    EnrichSource(
        key="ips",
        label="IPS lycées (data.education.gouv.fr)",
        value_columns=["IPS"],
        src_col="Source IPS", date_col="Date IPS",
        dataset_ref="fr-en-ips-lycees (indice de position sociale)",
        base_url="https://data.education.gouv.fr/api/explore/v2.1",
        uai_field_candidates=["uai", "identifiant_de_l_etablissement", "uai_etab"],
    ),
    EnrichSource(
        key="parcoursup",
        label="Parcoursup (offre de formations post-bac)",
        value_columns=["BTS ou post-bac"],
        src_col="Source post-bac", date_col="Date post-bac",
        dataset_ref="fr-esr-parcoursup (data.enseignementsup-recherche.gouv.fr)",
        base_url="https://data.enseignementsup-recherche.gouv.fr/api/explore/v2.1",
        uai_field_candidates=["cod_uai", "uai", "etablissement_uai"],
        note="Présence O/N d'au moins une formation post-bac pour l'UAI.",
    ),
    EnrichSource(
        key="fermes",
        label="Établissements fermés (annuaire, champ etat)",
        value_columns=["État établissement"],
        src_col="Source état", date_col="Date état",
        dataset_ref="fr-en-annuaire-education (champ etat OUVERT/FERME)",
        base_url="https://data.education.gouv.fr/api/explore/v2.1",
        uai_field_candidates=["identifiant_de_l_etablissement", "uai"],
    ),
    EnrichSource(
        key="onisep_structures",
        label="ONISEP Idéo-Structures",
        value_columns=["Présent ONISEP structures"],
        src_col="Source structures", date_col="Date structures",
        dataset_ref="ideo-structures-denseignement-secondaire (opendata.onisep.fr)",
        base_url="https://opendata.onisep.fr",
        uai_field_candidates=["code_uai", "uai"],
    ),
    EnrichSource(
        key="sites",
        label="Sites officiels des établissements",
        value_columns=["Bureau des entreprises", "Forum ou événement orientation"],
        src_col="Source site", date_col="Date site",
        dataset_ref="Site web de l'établissement (colonne 'Site web' du socle)",
        note="Détection par mots-clés — bureau des entreprises / forum orientation.",
    ),
]


def source_by_key(key: str) -> EnrichSource:
    for s in SOURCE_SPECS:
        if s.key == key:
            return s
    raise KeyError(key)
