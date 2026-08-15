# -*- coding: utf-8 -*-
"""Score d'Opportunite Territoriale B1 NEXA - Etape 1."""
import json, csv

B = {b["bassin"]: b for b in json.load(open("bassins.json"))}

# ---------------------------------------------------------------------------
# AXE AFFINITE + ECONOMIE NUMERIQUE
# NATURE : ESTIMATION EXPERTE (1-5), fondee sur le tissu economique et industriel
# documente de chaque territoire. NE SONT PAS des donnees DEPP.
# A remplacer par les effectifs reels NSI / STI2D / CIEL / STMG via pipeline/.
# ---------------------------------------------------------------------------
EXP = {
 # bassin            cyb dev data mkt eco  justification (ancrage factuel)
 "Marseille":         (5,5,5,4,5,"2e ville de France ; 4e hub internet europeen (cables sous-marins, data centers), CMA CGM, STMicroelectronics Rousset, Airbus Helicopters ; Aix-Marseille Universite"),
 "Bordeaux":          (4,5,4,5,5,"Capitale French Tech ; Cdiscount, Ubisoft, aeronautique-defense-spatial (Dassault, Thales, ArianeGroup) ; vin et tourisme = fort vivier marketing"),
 "Nantes":            (4,5,4,5,5,"Capitale French Tech, Atlanpole et quartier de la creation ; Airbus, forte densite d'ESN ; premier ecosysteme numerique de l'Ouest"),
 "Toulon":            (5,3,3,3,3,"1er port militaire francais : Marine nationale, Naval Group, cyberdefense navale ; Universite de Toulon"),
 "Saint-Nazaire":     (3,3,3,3,3,"Chantiers de l'Atlantique, Airbus, eolien offshore : industrie lourde a forts besoins de numerisation"),
 "Cholet":            (3,3,2,3,2,"Tissu tres dense de PME industrielles (mecanique, agroalimentaire, mode) ; offre superieure locale limitee"),
 "Toulouse":          (5,5,5,4,5,"Aeronautique-spatial (Airbus, Thales, CNES), 1er bassin d'emploi ingenieur hors IDF"),
 "Nice":              (5,5,4,4,5,"Sophia Antipolis, 1er technopole europeen ; Amadeus, Orange Labs ; economie touristique = vivier marketing"),
 "Montpellier":       (4,5,4,4,4,"IBM, Dell, sante-numerique ; corridor Montpellier-Nimes tres dynamique demographiquement"),
 "Strasbourg":        (4,4,4,4,4,"Capitale europeenne, banque-assurance, industrie ; ecosysteme numerique structure"),
 "Rouen":             (4,3,3,3,3,"Chimie-industrie-logistique portuaire, assurance (Matmut) ; besoins IT industriels"),
 "Rennes":            (5,5,4,4,5,"Pole cyber national (COMCYBER, DGA-MI, campus cyber breton), b<>com, telecoms"),
 "Annecy":            (3,4,3,4,4,"Mecatronique-decolletage vallee de l'Arve, frontalier Geneve, tertiaire haut de gamme"),
 "Metz":              (3,3,3,3,3,"Siderurgie-logistique, frontalier Luxembourg (emploi transfrontalier tres attractif)"),
 "Grenoble":          (5,5,5,3,5,"Microelectronique CEA-Leti, STMicroelectronics ; hub deeptech de rang mondial"),
 "Saint-Denis":       (3,4,3,4,3,"La Reunion : Capitale French Tech ; forte demande numerique locale, eloignement structurel"),
 "Avignon":           (3,3,3,4,2,"Agro-logistique-tourisme ; tissu numerique limite, vivier tertiaire important"),
 "Mulhouse":          (3,3,3,3,3,"Industrie automobile (Stellantis), textile, frontalier Bale-Suisse"),
 "Clermont-Ferrand":  (4,4,4,3,4,"Michelin (data/IA industrielle), Limagrain ; universite scientifique"),
 "Tours":             (3,4,3,4,3,"Banque-assurance, tertiaire superieur, universite ; bassin bien structure"),
 "Nancy":             (4,4,4,3,3,"LORIA (recherche informatique), industrie, universite de Lorraine"),
 "Angers":            (4,5,4,4,4,"Capitale French Tech, Cite de l'objet connecte, electronique-IoT, Thales"),
 "Caen":              (4,4,3,3,3,"Normandie Capitale French Tech 2026, NXP, Orange Labs, filiere cyber normande"),
 "Perpignan":         (2,2,2,4,2,"Tourisme-agriculture ; tissu numerique faible mais gros etablissements scolaires"),
 "Orléans":           (3,3,3,4,3,"Logistique, cosmetique, tertiaire ; effet de desserrement francilien"),
 "Brest":             (5,4,4,3,4,"Capitale French Tech Brest Bretagne Ouest ; cyberdefense navale, Naval Group, Thales, IMT Atlantique"),
 "Béziers":           (2,2,2,4,1,"Tourisme-viticulture ; economie numerique tres faible, vivier surtout tertiaire et pro"),
 "Valence":           (3,3,3,3,3,"Valence-Romans : industrie, electronique, nucleaire ; corridor rhodanien"),
 "Le Havre":          (4,3,3,3,3,"1er port francais : cybersecurite portuaire et logistique, industrie"),
 "Dijon":             (3,4,4,4,3,"OnDijon (smart city), agro-sante, universite ; tertiaire regional"),
 "Le Mans":           (3,3,4,3,3,"Assurance (groupe Covea/MMA) : gros besoins data et IT ; industrie automobile"),
 "Reims":             (3,3,3,4,2,"Champagne-agro-logistique ; tissu numerique modeste, tertiaire important"),
 "La Rochelle":       (3,4,4,4,3,"Ecosysteme French Tech, universite, port ; territoire pilote sur la donnee environnementale"),
 "Chambéry":          (3,4,3,3,3,"Savoie Technolac, energies, tourisme ; tissu tech de taille moyenne"),
 "Bayonne":           (3,4,3,5,3,"French Tech Pays Basque ; economie de marque, tourisme, sport-glisse = vivier marketing fort"),
 "Dunkerque":         (3,3,3,3,3,"Reindustrialisation majeure (gigafactories batteries), logistique transmanche : besoins IT emergents"),
 "Amiens":            (3,3,3,3,2,"Industrie et universite ; tissu numerique limite, effet de proximite francilienne"),
 "Fort-de-France":    (2,3,2,4,2,"Martinique : tertiaire-administration, eloignement maximal, offre superieure numerique reduite"),
 "Belfort":           (4,4,4,2,3,"Alstom, GE, Stellantis Sochaux, UTBM : bassin tres technique et industriel"),
 "Pau":               (4,4,5,3,4,"TotalEnergies et supercalculateur Pangea : l'un des plus gros centres de calcul prives d'Europe"),
 "Vannes":            (5,4,3,4,4,"Pole cyber breton (Vannes-Ploermel), DGA, Universite Bretagne Sud, ESN"),
 "Les Abymes":        (2,3,2,4,2,"Guadeloupe : eloignement, offre superieure numerique reduite, tertiaire dominant"),
 "Limoges":           (3,3,3,3,2,"Legrand, ceramique, universite ; economie numerique peu dense"),
 "Poitiers":          (3,4,4,4,3,"Futuroscope (image-numerique), laboratoire informatique universitaire, mutuelles proches"),
 "Quimper":           (2,3,2,3,2,"Agroalimentaire et tourisme ; tissu numerique faible"),
 "Évreux":            (2,2,2,3,2,"Pharma-cosmetique, sous-traitance ; forte dependance francilienne"),
 "Besançon":          (4,4,4,3,3,"Microtechniques, FEMTO-ST, biomedical : culture technique tres marquee"),
 "Saint-Brieuc":      (2,3,2,3,2,"Agroalimentaire ; tissu numerique faible, offre superieure limitee"),
 "Colmar":            (2,3,2,3,2,"Industrie et viticulture ; bassin dense mais peu tech"),
 "Lorient":           (4,4,3,3,3,"Naval Group, cyberdefense navale, Universite Bretagne Sud, pole mer"),
 "Forbach":           (2,2,2,3,1,"Bassin houiller en reconversion, frontalier Sarre ; economie numerique tres faible"),
 "Montélimar":        (3,2,2,3,2,"Nucleaire (Tricastin), agro ; bassin etale et peu tech"),
 "Mamoudzou":         (2,3,2,3,1,"Mayotte : demographie la plus jeune de France, offre superieure quasi inexistante"),
 "Saint-Quentin":     (2,2,2,3,1,"Industrie en reconversion ; economie numerique tres faible"),
 "Saint-Malo":        (2,3,2,4,2,"Tourisme et agro ; tissu numerique faible, vivier tertiaire"),
 # --- ajouts hors seuil de population : test explicite de H7 (villes moyennes) ---
 "Troyes":            (4,4,3,4,3,"Universite de technologie de Troyes (ingenierie info et cyber), logistique-textile"),
 "Angoulême":         (3,4,3,5,3,"Pole Magelis : image animee, jeu video, BD - vivier creatif et numerique atypique"),
 "Niort":             (4,5,5,4,4,"Capitale de la mutualite (MAIF, MACIF, MAAF, Groupama) : besoins IT et data massifs, Niort Tech"),
 "Albi":              (3,3,3,3,2,"IMT Mines Albi, agro ; bassin moyen a culture d'ingenierie"),
}

def conc_score(b):
    c = b["conc_20km_pct"]
    e = max(0.0, min(100.0, 100*(60 - b["etendue_km"])/35))   # 25 km -> 100 ; 60 km -> 0
    v = min(b["nb_villes_10k"], 10)/10*100
    return 0.40*c + 0.35*e + 0.25*v

UNIVERS_H7 = ("Troyes", "Angoulême", "Niort", "Albi", "Saint-Malo")  # ajouts sous seuil : rendent H7 testable
attendu = {n for n, b in B.items() if b["pop_bassin"] >= 250000} | set(UNIVERS_H7)
manquants = sorted(attendu - set(EXP))
if manquants:
    raise SystemExit(f"Bassins de l'univers sans evaluation experte : {manquants}")
en_trop = sorted(set(EXP) - attendu)
if en_trop:
    raise SystemExit(f"Bassins evalues hors univers : {en_trop}")
print(f"[univers] {len(EXP)} bassins scores "
      f"({len(attendu)-len(UNIVERS_H7)} de >= 250 000 hab. + {len(UNIVERS_H7)} villes moyennes pour H7)")

rows = []
for nom, (cy, dv, da, mk, ec, why) in EXP.items():
    b = B[nom]
    rows.append(dict(b, cyber=cy, dev=dv, data=da, mkt=mk, eco=ec, why=why,
                     affinite=(cy+dv+da+mk)/4, conc=conc_score(b)))

tmax = max(r["tle_estim"] for r in rows); tmin = min(r["tle_estim"] for r in rows)
import math
def viv(r):  # racine carree : limite le biais metropolitain sans l'annuler
    return 100*(math.sqrt(r["tle_estim"])-math.sqrt(tmin))/(math.sqrt(tmax)-math.sqrt(tmin))

for r in rows:
    r["s_vivier"] = viv(r)
    r["s_affinite"] = (r["affinite"]-1)/4*100
    r["s_conc"] = r["conc"]
    r["s_eco"] = (r["eco"]-1)/4*100
    r["score"] = round(0.40*r["s_vivier"] + 0.25*r["s_affinite"] + 0.20*r["s_conc"] + 0.15*r["s_eco"], 1)

rows.sort(key=lambda r: -r["score"])
for i, r in enumerate(rows):
    r["rang"] = i+1
    r["priorite"] = "P1" if i < 12 else ("P2" if i < 30 else "P3/TEST")

# profil dominant par filiere
for r in rows:
    m = max(r["cyber"], r["dev"], r["data"], r["mkt"])
    dom = [n for n, v in (("Cyber",r["cyber"]),("Dev",r["dev"]),("Data/IA",r["data"]),("Marketing",r["mkt"])) if v == m]
    r["filieres_dominantes"] = "+".join(dom)

json.dump(rows, open("bassins_scores.json","w"), ensure_ascii=False, indent=1)
cols = ["rang","bassin","priorite","regions","departements","villes_principales","pop_bassin","tle_estim",
        "nb_communes","nb_villes_10k","etendue_km","conc_20km_pct","cyber","dev","data","mkt",
        "filieres_dominantes","eco","d_campus_nexa_km","campus_proche","d_pole_etudiant_km",
        "contient_pole_etudiant","s_vivier","s_affinite","s_conc","s_eco","score","why"]
with open("bassins_scores.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(cols)
    for r in rows:
        w.writerow([("|".join(r[c]) if isinstance(r.get(c), list) else
                     (round(r[c],1) if isinstance(r.get(c), float) else r.get(c,""))) for c in cols])

print(f"{'#':>3} {'bassin':<18}{'prio':<8}{'score':>6}{'Tle~':>7}{'viv':>5}{'aff':>5}{'con':>5}{'eco':>5}  {'filieres':<18}{'dEtu':>6}")
for r in rows:
    print(f"{r['rang']:>3} {r['bassin']:<18}{r['priorite']:<8}{r['score']:>6}{r['tle_estim']:>7,}"
          f"{r['s_vivier']:>5.0f}{r['s_affinite']:>5.0f}{r['s_conc']:>5.0f}{r['s_eco']:>5.0f}  "
          f"{r['filieres_dominantes']:<18}{r['d_pole_etudiant_km']:>6.0f}")
