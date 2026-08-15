# -*- coding: utf-8 -*-
"""
ETAPE 1 / SCRIPT 5 - Enrichissement par les donnees reelles de l'Education nationale.

CE SCRIPT REMPLACE LES PROXYS DE L'ETAPE 1 PAR DES DONNEES OBSERVEES.

Il n'a PAS pu etre execute lors de la production de l'etude : l'environnement de
travail bloquait tout acces reseau vers data.education.gouv.fr (voir
05-limites-et-sources.md). Les colonnes suivantes du livrable sont donc, en l'etat,
des PROXYS ou des ESTIMATIONS EXPERTES explicitement signalees :

  - tle_estim        -> PROXY (population x ratio national 1,05 %)
  - cyber/dev/data/mkt -> ESTIMATION EXPERTE (tissu economique), non issue de la DEPP
  - nb_lycees        -> NON COLLECTE
  - IPS, Campus connecte, offre superieure locale -> NON COLLECTES

Lancer ce script depuis un poste disposant d'un acces sortant normal remplit ces
colonnes avec les effectifs reels par etablissement, agreges au bassin.

API : Opendatasoft Explore v2.1 (data.education.gouv.fr).
Les noms de champs des jeux DEPP evoluent d'un millesime a l'autre : le script
introspecte le schema de chaque dataset et affiche les champs disponibles avant
d'agreger, plutot que de supposer une structure figee.

Usage :
    python3 05_enrichissement_depp.py --inspect          # liste les champs de chaque dataset
    python3 05_enrichissement_depp.py --run              # telecharge et agrege par bassin
"""
import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets"

DATASETS = {
    # cle logique                  : (dataset_id, usage)
    "annuaire": ("fr-en-annuaire-education",
                 "Localisation des etablissements (lat/lon, commune, nature, secteur)"),
    "lycee_gt": ("fr-en-lycee_gt-effectifs-niveau-sexe-lv",
                 "Effectifs lycee general et technologique par niveau (dont Terminale)"),
    "lycee_pro": ("fr-en-lycee_pro-effectifs-niveau-sexe-lv",
                  "Effectifs lycee professionnel par niveau (dont Terminale pro)"),
    "specialites": ("fr-en-effectifs-specialites-doublettes-terminale-generale",
                    "Effectifs par enseignement de specialite en Terminale generale (dont NSI, Maths)"),
    "ips_lycees": ("fr-en-ips-lycees",
                   "Indice de position sociale par lycee (VARIABLE EXPERIMENTALE - hors scoring)"),
}

# Rattachement des specialites / series aux quatre familles NEXA.
# Ponderation = contribution d'un eleve de ce profil au vivier de la famille.
# Ce sont des HYPOTHESES d'affinite, a reviser avec les resultats commerciaux de l'annee 1.
AFFINITE = {
    "cyber":     {"NSI": 1.0, "STI2D": 0.6, "CIEL": 1.0, "MATHS": 0.3, "PHYSIQUE-CHIMIE": 0.2},
    "dev":       {"NSI": 1.0, "STI2D": 0.5, "CIEL": 0.7, "MATHS": 0.4, "PHYSIQUE-CHIMIE": 0.2},
    "data_ia":   {"NSI": 0.8, "MATHS": 1.0, "STI2D": 0.3, "PHYSIQUE-CHIMIE": 0.3, "SES": 0.2},
    "marketing": {"STMG": 1.0, "SES": 0.8, "HGGSP": 0.4, "LLCE": 0.3, "TLE_GENERALE_AUTRE": 0.2},
}

RAYON_BASSIN_KM = 30.0
R = 6371.0088


def api(path, **params):
    url = f"{BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read())


def inspect():
    for key, (ds, usage) in DATASETS.items():
        print(f"\n=== {key} : {ds}")
        print(f"    {usage}")
        try:
            meta = api(ds)
            fields = [f["name"] for f in meta.get("fields", [])]
            print(f"    {len(fields)} champs : {', '.join(fields)}")
        except Exception as exc:  # noqa: BLE001
            print(f"    ERREUR : {exc}", file=sys.stderr)
            print("    -> verifier l'acces reseau vers data.education.gouv.fr "
                  "et l'existence du dataset_id.")


def fetch_all(ds, select=None, where=None, page=100):
    """Pagination complete d'un dataset Opendatasoft."""
    out, offset = [], 0
    while True:
        params = {"limit": page, "offset": offset}
        if select:
            params["select"] = select
        if where:
            params["where"] = where
        data = api(f"{ds}/records", **params)
        results = data.get("results", [])
        out.extend(results)
        total = data.get("total_count", 0)
        offset += page
        if offset >= total or not results:
            break
        if offset % 2000 == 0:
            print(f"      {offset}/{total}...")
            time.sleep(0.2)
    return out


def hav(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    h = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))


def run():
    bassins = json.load(open("bassins.json"))
    print(f"[bassins] {len(bassins)} bassins charges depuis bassins.json")

    print("\n[1] Annuaire de l'education (lycees geolocalises)...")
    etabs = fetch_all(
        DATASETS["annuaire"][0],
        where='type_etablissement="Lycée"',
    )
    print(f"    {len(etabs)} lycees recuperes")

    print("\n[2] Effectifs lycees GT et pro...")
    gt = fetch_all(DATASETS["lycee_gt"][0])
    pro = fetch_all(DATASETS["lycee_pro"][0])
    print(f"    GT : {len(gt)} lignes | PRO : {len(pro)} lignes")

    print("\n[3] Specialites Terminale generale...")
    spe = fetch_all(DATASETS["specialites"][0])
    print(f"    {len(spe)} lignes")

    # -- rattachement de chaque etablissement a un bassin (plus proche pole <= 30 km)
    print("\n[4] Rattachement etablissements -> bassins...")
    for e in etabs:
        lat, lon = e.get("latitude"), e.get("longitude")
        e["_bassin"] = None
        if lat is None or lon is None:
            continue
        best, bd = None, RAYON_BASSIN_KM
        for b in bassins:
            d = hav((lat, lon), (b["lat"], b["lon"]))
            if d <= bd:
                best, bd = b["bassin"], d
        e["_bassin"] = best
    rattaches = sum(1 for e in etabs if e["_bassin"])
    print(f"    {rattaches}/{len(etabs)} lycees rattaches a un bassin")

    json.dump({"etablissements": etabs, "effectifs_gt": gt, "effectifs_pro": pro,
               "specialites": spe},
              open("depp_brut.json", "w"), ensure_ascii=False)
    print("\n[OK] depp_brut.json ecrit.")
    print("Etape suivante : agreger par bassin en utilisant les noms de champs reels")
    print("(lancer --inspect pour les lister) puis recalculer 03_scoring.py avec :")
    print("  - tle_reel        a la place de tle_estim (PROXY)")
    print("  - potentiel_cyber / _dev / _data_ia / _marketing calcules via AFFINITE")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true", help="lister les champs des datasets")
    ap.add_argument("--run", action="store_true", help="telecharger et rattacher")
    args = ap.parse_args()
    if args.inspect:
        inspect()
    elif args.run:
        run()
    else:
        ap.print_help()
