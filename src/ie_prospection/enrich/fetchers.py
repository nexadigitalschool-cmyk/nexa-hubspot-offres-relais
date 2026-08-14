"""Récupération des sources publiques (best-effort, dégradation propre).

Chaque fetcher tente d'interroger la source réelle. En cas d'indisponibilité
(réseau bloqué, dataset introuvable, champ renommé), il renvoie un résultat
``available=False`` avec le message d'erreur : l'étape se poursuit alors avec
des valeurs vides, documentées. Toutes les correspondances se font sur l'UAI.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import requests

from ..config import HttpConfig
from ..logging_utils import get_logger
from ..ods_client import ODSAPIError, ODSClient
from .schema2 import EnrichSource

# Identifiants de datasets concrets (à confirmer au 1er run en ligne).
ODS_DATASET_IDS = {
    "effectifs": "fr-en-lycee_gt-effectifs-niveau-sexe-lv",
    "ips": "fr-en-ips-lycees",
    "parcoursup": "fr-esr-parcoursup",
    "fermes": "fr-en-annuaire-education",
    "onisep_structures": "ideo-structures-denseignement-secondaire",
    "onisep_formations": "ideo-formations-initiales-en-france",
}

# Mots-clés de détection sur les sites officiels.
KW_BDE = ("bureau des entreprises", "bureau des entreprise", "bde ", "relation entreprises")
KW_FORUM = ("forum orientation", "forum de l'orientation", "forum des métiers",
            "forum des metiers", "journée orientation", "semaine de l'orientation",
            "forum des formations")


@dataclass
class FetchResult:
    key: str
    label: str
    available: bool
    by_uai: dict[str, dict]
    source_ref: str
    date: str
    error: str | None = None
    matched: int = 0
    fields_resolved: dict = field(default_factory=dict)


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _ods_records_for_uais(base_url, dataset_id, uai_field_candidates, uais,
                          http: HttpConfig, raw_dir, label):
    """Récupère les enregistrements d'un dataset ODS pour une liste d'UAI,
    indexés par UAI. Lève ODSAPIError en cas d'échec non récupérable."""
    client = ODSClient(base_url, dataset_id, http, raw_dir)
    uai_field = client.resolve_field(uai_field_candidates) or uai_field_candidates[0]
    by_uai: dict[str, dict] = {}
    for chunk in _chunks(list(uais), 40):
        values = ", ".join('"' + u + '"' for u in chunk)
        where = f'{uai_field} in ({values})'
        for rec in client.iter_records(where, label=f"{label}", resume=True):
            u = str(rec.get(uai_field, "")).strip()
            if u:
                by_uai[u] = rec
    return uai_field, by_uai


def fetch_ods_source(spec: EnrichSource, uais, http, raw_dir, derive) -> FetchResult:
    log = get_logger()
    date = _today()
    dataset_id = ODS_DATASET_IDS.get(spec.key, "")
    try:
        uai_field, raw_by_uai = _ods_records_for_uais(
            spec.base_url, dataset_id, spec.uai_field_candidates, uais, http, raw_dir,
            label=f"enrich_{spec.key}")
    except (ODSAPIError, requests.RequestException, Exception) as exc:  # noqa: BLE001
        log.warning("Source « %s » indisponible : %s", spec.label, exc)
        return FetchResult(spec.key, spec.label, False, {}, dataset_id, date,
                           error=str(exc)[:300])
    by_uai = {u: derive(rec) for u, rec in raw_by_uai.items()}
    return FetchResult(spec.key, spec.label, True, by_uai, dataset_id, date,
                       matched=len(by_uai), fields_resolved={"uai": uai_field})


def fetch_websites(spec: EnrichSource, socle_rows, timeout=8.0) -> FetchResult:
    """Détecte bureau des entreprises / forum d'orientation sur le site officiel."""
    log = get_logger()
    date = _today()
    by_uai: dict[str, dict] = {}
    errors = 0
    checked = 0
    session = requests.Session()
    for row in socle_rows:
        url = (row.get("Site web") or "").strip()
        uai = row.get("UAI", "").strip()
        if not url or not uai:
            continue
        if not url.startswith("http"):
            url = "https://" + url
        checked += 1
        try:
            resp = session.get(url, timeout=timeout)
            html = resp.text.lower()
            by_uai[uai] = {
                "Bureau des entreprises": "O" if any(k in html for k in KW_BDE) else "N",
                "Forum ou événement orientation": "O" if any(k in html for k in KW_FORUM) else "N",
            }
        except Exception as exc:  # noqa: BLE001
            errors += 1
            log.debug("Site injoignable pour UAI %s (%s) : %s", uai, url, exc)
    available = checked > 0 and errors < checked
    err = None if available else f"{errors}/{checked} sites injoignables"
    if not available:
        log.warning("Source « %s » indisponible : %s", spec.label, err)
    return FetchResult(spec.key, spec.label, available, by_uai,
                       "Sites officiels (colonne Site web)", date,
                       error=err, matched=len(by_uai))


# --- Fonctions de dérivation (raw record ODS -> colonnes de valeur) ----------
def derive_effectifs(rec: dict) -> dict:
    for k in ("effectif", "nombre_d_eleves", "nb_eleves", "effectif_total",
              "total_eleves"):
        if k in rec and str(rec[k]).strip() not in ("", "None"):
            return {"Effectif élèves": str(rec[k]).strip()}
    return {"Effectif élèves": ""}


def derive_ips(rec: dict) -> dict:
    for k in ("ips", "ips_ensemble_gt_pro", "ips_voie_gt", "indice_de_position_sociale"):
        if k in rec and str(rec[k]).strip() not in ("", "None"):
            return {"IPS": str(rec[k]).strip()}
    return {"IPS": ""}


def derive_parcoursup(rec: dict) -> dict:
    # Présence de l'UAI dans Parcoursup => au moins une formation post-bac.
    return {"BTS ou post-bac": "O"}


def derive_fermes(rec: dict) -> dict:
    etat = ""
    for k in ("etat", "etat_etablissement"):
        if k in rec and str(rec[k]).strip():
            etat = str(rec[k]).strip()
            break
    up = etat.upper()
    val = "Fermé" if "FERM" in up else ("Actif" if "OUVERT" in up else etat)
    return {"État établissement": val}


def derive_onisep_structures(rec: dict) -> dict:
    return {"Présent ONISEP structures": "O"}


def derive_onisep_formations(rec: dict) -> dict:
    # Concatène les intitulés de formation disponibles pour repérer les filières.
    blob = " ".join(str(v) for v in rec.values()).lower()
    def has(*keys):
        return "O" if any(k in blob for k in keys) else "N"
    return {
        "Filière NSI": has("numérique et sciences informatiques", "nsi"),
        "Filière SNT": has("sciences numériques et technologie", "snt"),
        "Filière STI2D": has("sti2d", "sciences et technologies de l'industrie"),
        "Filière STMG": has("stmg", "sciences et technologies du management"),
        "Bac pro SN": has("systèmes numériques", "bac pro sn", "cybersécurité"),
    }


DERIVERS = {
    "effectifs": derive_effectifs,
    "ips": derive_ips,
    "parcoursup": derive_parcoursup,
    "fermes": derive_fermes,
    "onisep_structures": derive_onisep_structures,
    "onisep_formations": derive_onisep_formations,
}


def _today() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
