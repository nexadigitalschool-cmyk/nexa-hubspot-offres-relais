# -*- coding: utf-8 -*-
import json, math
import numpy as np
from gpsfix import build_gps

R = 6371.0088
RAYON = 30.0            # rayon d'activation commerciale d'un bassin IE
RAYON_EXCL = 60.0
POP_MIN_POLE = 15000
RATIO_TLE = 0.0105      # PROXY national Terminale(GT+pro)/population

CAMPUS_A = {"Paris":(48.8709,2.3646),"Lyon":(45.7578,4.8320),"Lille":(50.6216,3.0790)}
CAMPUS_B = dict(CAMPUS_A, **{"Bordeaux":(44.8672,-0.5560),"Nantes":(47.2043,-1.5535),"Marseille":(43.2555,5.3980)})
POLES_ETU = {
 "Paris":(48.8566,2.3522),"Lyon":(45.7640,4.8357),"Marseille":(43.2965,5.3698),"Toulouse":(43.6047,1.4442),
 "Lille":(50.6292,3.0573),"Bordeaux":(44.8378,-0.5792),"Nantes":(47.2184,-1.5536),"Montpellier":(43.6108,3.8767),
 "Strasbourg":(48.5734,7.7521),"Rennes":(48.1173,-1.6778),"Grenoble":(45.1885,5.7245),"Nice":(43.7102,7.2620),
 "Nancy":(48.6921,6.1844),"Clermont-Ferrand":(45.7772,3.0870),"Rouen":(49.4432,1.0999),"Dijon":(47.3220,5.0415),
 "Poitiers":(46.5802,0.3404),"Caen":(49.1829,-0.3707),"Reims":(49.2583,4.0317),"Angers":(47.4784,-0.5632),
 "Tours":(47.3941,0.6848),"Amiens":(49.8941,2.2958),"Besancon":(47.2378,6.0241),"Limoges":(45.8336,1.2611),
 "Brest":(48.3904,-4.4861),"Saint-Etienne":(45.4397,4.3872),"Orleans":(47.9029,1.9093),"Metz":(49.1193,6.1757),
 "Aix-en-Provence":(43.5297,5.4474),"Toulon":(43.1242,5.9280),"Le Mans":(48.0061,0.1996),"Pau":(43.2951,-0.3708),
 "Perpignan":(42.6887,2.8948),"La Rochelle":(46.1591,-1.1520),"Avignon":(43.9493,4.8055),"Mulhouse":(47.7508,7.3359),
 "Chambery":(45.5646,5.9178),"Le Havre":(49.4944,0.1079),"Lorient":(47.7482,-3.3702),"Troyes":(48.2973,4.0744),
 "Valenciennes":(50.3583,3.5233),"Nimes":(43.8367,4.3601),"Saint-Denis-Reunion":(-20.8823,55.4504),
 "Fort-de-France":(14.6161,-61.0588),"Pointe-a-Pitre":(16.2410,-61.5330),"La Roche-sur-Yon":(46.6706,-1.4269),
 "Cergy":(49.0339,2.0782),"Compiegne":(49.4179,2.8261),"Albi":(43.9298,2.1480),"Annecy":(45.8992,6.1294),
}

deps_nom = {d["code"]: d["nom"] for d in json.load(open("deco/package/data/departements.json"))}
regs_nom = {r["code"]: r["nom"] for r in json.load(open("deco/package/data/regions.json"))}

etalab = json.load(open("deco/package/data/communes.json"))
gps = build_gps()

C = [c for c in etalab if c.get("type")=="commune-actuelle" and c.get("population") and gps.get(c["code"])]
noms = [c["nom"] for c in C]
pops = np.array([c["population"] for c in C], float)
deps = [c.get("departement","") for c in C]
regs = [c.get("region","") for c in C]
lats = np.array([gps[c["code"]][0] for c in C]); lons = np.array([gps[c["code"]][1] for c in C])
rlat = np.radians(lats)

def dist_all(plat, plon):
    p2 = math.radians(plat)
    h = np.sin((p2-rlat)/2)**2 + np.cos(rlat)*math.cos(p2)*np.sin(np.radians(plon-lons)/2)**2
    return 2*R*np.arcsin(np.sqrt(h))

d_A = np.min(np.vstack([dist_all(*v) for v in CAMPUS_A.values()]), axis=0)
d_B = np.min(np.vstack([dist_all(*v) for v in CAMPUS_B.values()]), axis=0)
excl_A, excl_B = d_A <= RAYON_EXCL, d_B <= RAYON_EXCL
d_etu = np.min(np.vstack([dist_all(*v) for v in POLES_ETU.values()]), axis=0)

print(f"[data] {len(C)} communes | pop {pops.sum():,.0f}")
print(f"[excl A Paris/Lyon/Lille] {excl_A.sum()} communes, {pops[excl_A].sum():,.0f} hab ({100*pops[excl_A].sum()/pops.sum():.1f}%)")
print(f"[excl B +Bdx/Nantes/Mrs ] {excl_B.sum()} communes, {pops[excl_B].sum():,.0f} hab ({100*pops[excl_B].sum()/pops.sum():.1f}%)")

elig = ~excl_A
cand = np.where(elig & (pops >= POP_MIN_POLE))[0]
D = np.vstack([dist_all(lats[i], lons[i]) for i in cand])
# pole = maximum local de population dans un rayon de 12 km (evite les bassins centres sur une banlieue)
locmax = np.array([pops[i] >= pops[np.where(D[k] <= 12)[0]].max() for k, i in enumerate(cand)])
cand_ok = np.where(locmax)[0]
print(f"[poles] candidats >= {POP_MIN_POLE} hab hors exclusion A : {len(cand)} -> maxima locaux : {len(cand_ok)}")

dispo = elig.copy(); out = []
while len(out) < 75:
    m = (D <= RAYON) & dispo[None, :]
    catch = (m * pops[None, :]).sum(axis=1)
    catch[~dispo[cand]] = 0
    catch[~locmax] = 0
    k = int(np.argmax(catch))
    if catch[k] < 110000: break
    memb = np.where(m[k])[0]
    order = memb[np.argsort(-pops[memb])]
    gros = [i for i in order if pops[i] >= 10000]
    et = 0.0
    for a in gros:
        for b in gros:
            dd = 2*R*math.asin(math.sqrt(math.sin((rlat[b]-rlat[a])/2)**2 +
                 math.cos(rlat[a])*math.cos(rlat[b])*math.sin(math.radians(lons[b]-lons[a])/2)**2))
            et = max(et, dd)
    pop_b = pops[memb].sum()
    main = order[0]   # ville principale du bassin : reference des distances
    dcs = {c: float(dist_all(*v)[main]) for c, v in CAMPUS_B.items()}
    dep_pop = {}
    for i in memb: dep_pop[deps[i]] = dep_pop.get(deps[i], 0) + pops[i]
    out.append({
      "bassin": noms[order[0]],
      "pole_calcul": noms[cand[k]],
      "lat": round(float(lats[cand[k]]),4), "lon": round(float(lons[cand[k]]),4),
      "lat_ville_principale": round(float(lats[order[0]]),4), "lon_ville_principale": round(float(lons[order[0]]),4),
      "pop_bassin": int(pop_b), "pop_ville_centre": int(pops[order[0]]),
      "nb_communes": int(len(memb)), "nb_villes_10k": len(gros),
      "villes_principales": [f"{noms[i]} ({int(round(pops[i]/1000))}k)" for i in order[:5]],
      "etendue_km": round(et,1),
      "conc_20km_pct": round(float(100*pops[memb][D[k][memb] <= 20].sum()/pop_b),1),
      "departements": [f"{d} {deps_nom.get(d,'')}" for d,_ in sorted(dep_pop.items(), key=lambda x:-x[1])],
      "regions": sorted({regs_nom.get(regs[i],"") for i in memb}),
      "tle_estim": int(round(pop_b*RATIO_TLE, -1)),
      "d_campus_nexa_km": round(min(dcs.values()),1),
      "campus_proche": min(dcs, key=dcs.get),
      "d_pole_etudiant_km": round(float(d_etu[main]),1),
      "contient_pole_etudiant": bool(min(d_etu[i] for i in memb) <= 10),
      "exclu_perimetre_B": bool(excl_B[order[0]]),
    })
    dispo[memb] = False

json.dump(out, open("bassins.json","w"), ensure_ascii=False, indent=1)
print(f"[bassins] {len(out)} bassins\n")
print(f"{'#':>3} {'bassin':<24}{'pop':>10}{'Tle~':>7}{'v10k':>5}{'etend':>7}{'c20':>6}{'dNEXA':>7}{'dEtu':>7} dep")
for i,b in enumerate(out,1):
    print(f"{i:>3} {b['bassin']:<24}{b['pop_bassin']:>10,}{b['tle_estim']:>7,}{b['nb_villes_10k']:>5}"
          f"{b['etendue_km']:>7.1f}{b['conc_20km_pct']:>6.0f}{b['d_campus_nexa_km']:>7.0f}{b['d_pole_etudiant_km']:>7.0f}"
          f" {','.join(d[:2] for d in b['departements'][:3])}{' [exclB]' if b['exclu_perimetre_B'] else ''}")
