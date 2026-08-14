"""Géocodage des adresses de campus via la Base Adresse Nationale (officielle).

On ne fabrique jamais de coordonnées : on résout une adresse RÉELLE fournie par
NEXA auprès d'une source officielle (``api-adresse.data.gouv.fr``). La provenance
est journalisée. En l'absence d'adresse OU si le service est injoignable, aucune
coordonnée n'est produite et le calcul de distance reste désactivé.
"""
from __future__ import annotations

import requests

from .logging_utils import get_logger

BAN_URL = "https://api-adresse.data.gouv.fr/search/"


def geocode_ban(address: str, session: requests.Session | None = None,
                timeout: float = 20.0) -> tuple[float, float] | None:
    """Retourne (latitude, longitude) WGS84 ou None si non résolu."""
    log = get_logger()
    sess = session or requests.Session()
    try:
        resp = sess.get(BAN_URL, params={"q": address, "limit": 1}, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # réseau, HTTP, JSON
        log.warning("Géocodage BAN indisponible pour « %s » : %s", address, exc)
        return None
    features = data.get("features") or []
    if not features:
        log.warning("Aucun résultat BAN pour « %s »", address)
        return None
    lon, lat = features[0]["geometry"]["coordinates"]  # BAN renvoie [lon, lat]
    score = features[0].get("properties", {}).get("score")
    log.info("Géocodage BAN « %s » -> lat=%.6f lon=%.6f (score=%s)",
             address, lat, lon, score)
    return float(lat), float(lon)
