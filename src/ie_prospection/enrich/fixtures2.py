"""Données d'enrichissement synthétiques (démonstration hors-ligne étape 2).

⚠️ SYNTHÉTIQUES et NON officielles. Elles reproduisent une couverture partielle
réaliste (jointures incomplètes, valeurs manquantes, quelques établissements
fermés) pour exercer les jointures UAI, le calcul des taux et les rapports.
Les colonnes Source portent la mention « FIXTURE ».
"""
from __future__ import annotations

import hashlib

from .fetchers import FetchResult, _today
from .schema2 import SOURCE_SPECS, source_by_key


def _h(salt: str, uai: str) -> int:
    return int(hashlib.md5((salt + uai).encode("utf-8")).hexdigest(), 16)


def _pct(salt: str, uai: str) -> int:
    return _h(salt, uai) % 100


def build_fixture_results(socle_rows) -> list[FetchResult]:
    uais = [r["UAI"] for r in socle_rows if r.get("UAI")]
    date = _today()
    results: list[FetchResult] = []

    def mk(key, by_uai, available=True, error=None):
        spec = source_by_key(key)
        return FetchResult(key, f"{spec.label} [FIXTURE]", available, by_uai,
                           f"FIXTURE:{spec.dataset_ref}", date,
                           error=error, matched=len(by_uai))

    # ONISEP structures : 95% présents.
    results.append(mk("onisep_structures",
                      {u: {"Présent ONISEP structures": "O"} for u in uais
                       if _pct("struct", u) < 95}))

    # ONISEP formations : 90% présents, filières dérivées.
    forms = {}
    for u in uais:
        if _pct("form", u) < 90:
            forms[u] = {
                "Filière NSI": "O" if _pct("nsi", u) < 45 else "N",
                "Filière SNT": "O" if _pct("snt", u) < 80 else "N",
                "Filière STI2D": "O" if _pct("sti", u) < 30 else "N",
                "Filière STMG": "O" if _pct("stmg", u) < 40 else "N",
                "Bac pro SN": "O" if _pct("bacpro", u) < 20 else "N",
            }
    results.append(mk("onisep_formations", forms))

    # Effectifs : 88% présents, dont quelques valeurs vides.
    eff = {}
    for u in uais:
        if _pct("eff", u) < 88:
            n = 200 + _h("effn", u) % 1400
            eff[u] = {"Effectif élèves": "" if _pct("effmiss", u) < 6 else str(n)}
    results.append(mk("effectifs", eff))

    # IPS : 85% présents.
    ips = {}
    for u in uais:
        if _pct("ips", u) < 85:
            ips[u] = {"IPS": str(85 + _h("ipsn", u) % 60)}
    results.append(mk("ips", ips))

    # Parcoursup : 60% ont une offre post-bac.
    ps = {u: {"BTS ou post-bac": "O"} for u in uais if _pct("ps", u) < 60}
    results.append(mk("parcoursup", ps))

    # État (annuaire etat) : présents pour ~99%, dont 2% fermés.
    fer = {}
    for u in uais:
        if _pct("etatpres", u) < 99:
            fer[u] = {"État établissement": "Fermé" if _pct("ferme", u) < 2 else "Actif"}
    results.append(mk("fermes", fer))

    # Sites officiels : analysés uniquement quand une URL existe ; ~85% des
    # sites présents sont effectivement exploitables (les autres injoignables).
    sites = {}
    for r in socle_rows:
        u = r.get("UAI", "")
        has_site = (r.get("Site web") or "").strip() != ""
        if u and has_site and _pct("site", u) < 85:
            sites[u] = {
                "Bureau des entreprises": "O" if _pct("bde", u) < 25 else "N",
                "Forum ou événement orientation": "O" if _pct("forum", u) < 35 else "N",
            }
    results.append(mk("sites", sites))

    return results
