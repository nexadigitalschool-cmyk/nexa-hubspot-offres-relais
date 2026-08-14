"""Cascade de sources publiques par établissement (respectant robots.txt).

Ordre imposé :
  1. site officiel de l'établissement ;
  2. site officiel de l'académie ;
  3. annuaire / source institutionnelle publique ;
  4. page professionnelle publique accessible sans connexion ;
  5. LinkedIn / Sales Navigator UNIQUEMENT si accès légal déjà configuré.

Chaque tentative est tracée (statut, détail) pour le rapport des sources.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import requests

from ..logging_utils import get_logger
from .extractors import extract_contacts
from .robots import RobotsPolicy
from .schema4 import MAX_CONTACTS_PER_ETAB

# Pages candidates typiques où figure l'équipe de direction.
CANDIDATE_PATHS = [
    "", "/direction", "/equipe-de-direction", "/l-equipe-de-direction",
    "/le-lycee/direction", "/etablissement", "/l-etablissement", "/contact",
]


@dataclass
class NominatifConfig:
    user_agent: str = "NEXA-IE-prospection-bot"
    timeout: float = 8.0
    max_pages_per_site: int = 4
    reconstruct_emails: bool = True
    enable_linkedin: bool = False           # OFF par défaut (accès légal requis)
    academie_directories: dict = field(default_factory=dict)  # académie -> URL


@dataclass
class SourceAttempt:
    step: int
    source: str
    url: str
    status: str        # ok | blocked_robots | network_error | http_error | empty | not_configured
    detail: str
    uai: str = ""


def _fetch(url, policy: RobotsPolicy, session, cfg) -> tuple[str | None, str, str]:
    allowed, reason = policy.can_fetch(url)
    if not allowed:
        return None, "blocked_robots", reason
    try:
        resp = session.get(url, timeout=cfg.timeout,
                           headers={"User-Agent": cfg.user_agent})
    except Exception as exc:  # noqa: BLE001
        return None, "network_error", str(exc)[:200]
    if resp.status_code >= 400:
        return None, "http_error", f"HTTP {resp.status_code}"
    if not resp.text.strip():
        return None, "empty", "réponse vide"
    return resp.text, "ok", "ok"


def gather_for_etab(etab: dict, cfg: NominatifConfig, policy: RobotsPolicy,
                    session, date: str) -> tuple[list[dict], list[SourceAttempt]]:
    log = get_logger()
    uai = etab.get("UAI", "").strip()
    generic_email = etab.get("Mail ce.", "").strip()
    contacts: dict[tuple, dict] = {}
    attempts: list[SourceAttempt] = []

    def add(new):
        for c in new:
            k = (c["UAI établissement"], c["Prénom"].lower(), c["Nom"].lower(), c["Rôle"])
            contacts.setdefault(k, c)

    # --- 1. Site officiel de l'établissement --------------------------------
    site = (etab.get("Site web") or "").strip()
    if site:
        base = site if site.startswith("http") else "https://" + site
        base = base.rstrip("/")
        pages = 0
        for path in CANDIDATE_PATHS:
            if pages >= cfg.max_pages_per_site or len(contacts) >= MAX_CONTACTS_PER_ETAB:
                break
            url = base + path
            html, status, detail = _fetch(url, policy, session, cfg)
            attempts.append(SourceAttempt(1, "Site officiel établissement", url,
                                          status, detail, uai))
            if status == "ok":
                pages += 1
                add(extract_contacts(html, url, uai, "Site officiel établissement",
                                     date, generic_email, cfg.reconstruct_emails))
    else:
        attempts.append(SourceAttempt(1, "Site officiel établissement", "",
                                      "not_configured", "pas d'URL de site", uai))

    # --- 2. Site officiel de l'académie -------------------------------------
    aca = etab.get("Académie", "")
    aca_url = cfg.academie_directories.get(aca)
    if len(contacts) < MAX_CONTACTS_PER_ETAB and aca_url:
        url = aca_url.replace("{uai}", uai)
        html, status, detail = _fetch(url, policy, session, cfg)
        attempts.append(SourceAttempt(2, "Site académie", url, status, detail, uai))
        if status == "ok":
            add(extract_contacts(html, url, uai, "Site académie", date,
                                 generic_email, cfg.reconstruct_emails))
    else:
        attempts.append(SourceAttempt(2, "Site académie", "", "not_configured",
                                      "annuaire académie non configuré", uai))

    # --- 3. Annuaire / source institutionnelle publique ---------------------
    attempts.append(SourceAttempt(3, "Annuaire institutionnel", "", "not_configured",
                                  "source institutionnelle nominative non configurée", uai))

    # --- 4. Page professionnelle publique -----------------------------------
    attempts.append(SourceAttempt(4, "Page professionnelle publique", "",
                                  "not_configured",
                                  "recherche web non configurée / non autorisée ici", uai))

    # --- 5. LinkedIn / Sales Navigator (si accès légal configuré) -----------
    if cfg.enable_linkedin:
        attempts.append(SourceAttempt(5, "LinkedIn / Sales Navigator", "",
                                      "not_configured",
                                      "connecteur légal non branché dans ce run", uai))
    else:
        attempts.append(SourceAttempt(5, "LinkedIn / Sales Navigator", "", "skipped",
                                      "désactivé (aucun accès légal configuré)", uai))

    # Tri par priorité de rôle + plafond à 5 contacts.
    ordered = sorted(contacts.values(), key=lambda c: c.get("_priority", 99))
    ordered = ordered[:MAX_CONTACTS_PER_ETAB]
    for c in ordered:
        c.pop("_priority", None)
    if not ordered:
        log.debug("UAI %s : aucun contact nominatif trouvé", uai)
    return ordered, attempts
