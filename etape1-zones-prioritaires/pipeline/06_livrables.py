# -*- coding: utf-8 -*-
"""ETAPE 1 / SCRIPT 6 - Generation du tableau de synthese et du handoff etape 2."""
import json, os

rows = json.load(open("bassins_scores.json"))
os.makedirs("out", exist_ok=True)

def note(v):  # 1-5 -> notation lisible
    return "•" * int(v) + "·" * (5 - int(v))

lines = []
lines.append("| # | Zone / bassin | Prio | Région(s) | Départements | Villes principales | Vivier B1 (Tle est.) | Affinité | Cyber | Dev | Data/IA | Mkt | Concentration | Éco. num. | Score | Filières dominantes | Pourquoi |")
lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    reg = ", ".join(x for x in r["regions"] if x)[:38]
    dep = ", ".join(d.split(" ")[0] for d in r["departements"][:4])
    vil = ", ".join(v.split(" (")[0] for v in r["villes_principales"][:3])
    tle = f"{r['tle_estim']:,}".replace(",", " ")
    lines.append(
        f"| {r['rang']} | **{r['bassin']}** | {r['priorite']} | {reg} | {dep} | {vil} | "
        f"~{tle} | {r['s_affinite']:.0f}/100 | {note(r['cyber'])} | {note(r['dev'])} | "
        f"{note(r['data'])} | {note(r['mkt'])} | {r['s_conc']:.0f}/100 | {note(r['eco'])} | "
        f"**{r['score']}** | {r['filieres_dominantes']} | {r['why']} |"
    )
open("out/tableau_bassins.md", "w").write("\n".join(lines))

def hypos(r):
    h = []
    if not r["contient_pole_etudiant"]:
        h.append("H1 - faible offre superieure locale : la zone convertit-elle mieux ?")
        h.append(f"H2 - eloignement du pole etudiant majeur ({r['d_pole_etudiant_km']:.0f} km)")
    else:
        h.append("H1 (contre-test) - offre superieure locale forte : la zone convertit-elle malgre la concurrence ?")
    if r["eco"] >= 4:
        h.append("H3 - economie numerique dynamique : effet sur l'interet pour NEXA")
    if r["eco"] <= 2:
        h.append("H3 (contre-test) - economie numerique faible : le vivier suffit-il seul ?")
    if r["eco"] == 3 and max(r["cyber"], r["dev"]) >= 4:
        h.append("H4 - besoins IT reels sans ecosysteme startup : effet sur l'alternance plutot que le recrutement")
    if max(r["cyber"], r["dev"]) >= 4:
        h.append("H5 - concentration NSI/STI2D/CIEL supposee : surperformance Cyber/Dev a verifier sur donnees DEPP")
    if r["mkt"] >= 4:
        h.append("H6 - vivier STMG/generaliste suppose : performance Marketing Digital a verifier")
    if r["pop_bassin"] < 400000:
        h.append("H7 - ville moyenne : rendement par IE superieur aux metropoles ?")
    h.append("H8 - presence d'un Campus connecte : A COLLECTER (DGESIP) avant lancement")
    return h

# --- handoff etape 2 -------------------------------------------------------
handoff = []
for r in rows:
    handoff.append({
        "bassin": r["bassin"],
        "priorite": r["priorite"],
        "rang": r["rang"],
        "perimetre": {
            "pole_centre": {"commune": r["pole_calcul"], "lat": r["lat"], "lon": r["lon"]},
            "rayon_km": 30,
            "departements": r["departements"],
            "regions": r["regions"],
            "villes_principales": r["villes_principales"],
            "nb_communes": r["nb_communes"],
        },
        "potentiel_estime": {
            "population_bassin": r["pop_bassin"],
            "terminale_estimee": r["tle_estim"],
            "nature": "PROXY population x 1,05 % - a remplacer par effectifs DEPP",
        },
        "filieres_nexa_prioritaires": r["filieres_dominantes"].split("+"),
        "potentiels_par_filiere_1a5": {"cyber": r["cyber"], "developpement": r["dev"],
                                       "data_ia": r["data"], "marketing": r["mkt"],
                                       "nature": "ESTIMATION EXPERTE"},
        "raisons_de_selection": r["why"],
        "variables_experimentales": {
            "distance_pole_etudiant_majeur_km": r["d_pole_etudiant_km"],
            "contient_pole_etudiant_majeur": r["contient_pole_etudiant"],
            "distance_campus_nexa_km": r["d_campus_nexa_km"],
            "campus_nexa_le_plus_proche": r["campus_proche"],
            "concentration_20km_pct": r["conc_20km_pct"],
            "etendue_villes_km": r["etendue_km"],
            "campus_connecte": "A_COLLECTER (source DGESIP)",
            "offre_superieure_numerique_locale": "A_COLLECTER (Parcoursup / ONISEP)",
            "ips_moyen_lycees": "A_COLLECTER (fr-en-ips-lycees)",
        },
        "hypotheses_a_tester": hypos(r),
    })
json.dump(handoff, open("out/handoff_etape2.json", "w"), ensure_ascii=False, indent=1)
print("out/tableau_bassins.md et out/handoff_etape2.json generes")
print("bassins:", len(rows), "| P1:", sum(1 for r in rows if r["priorite"]=="P1"),
      "| P2:", sum(1 for r in rows if r["priorite"]=="P2"),
      "| P3/TEST:", sum(1 for r in rows if r["priorite"]=="P3/TEST"))
