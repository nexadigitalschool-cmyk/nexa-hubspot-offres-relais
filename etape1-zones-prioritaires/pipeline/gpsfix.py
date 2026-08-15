"""Complement de geolocalisation : Paris / Lyon / Marseille sont codes par arrondissement
dans le referentiel La Poste. Centroide = moyenne des arrondissements (source La Poste)."""
import json
def build_gps():
    gps, arr = {}, {"75056": [], "69123": [], "13055": []}
    pref = {"751": "75056", "693": "69123", "132": "13055"}
    for r in json.load(open("communes.json")):
        g = r.get("coordonnees_gps") or ""
        if "," not in g: continue
        try: la, lo = [float(x) for x in g.split(",")]
        except ValueError: continue
        code = str(r["Code_commune_INSEE"]).zfill(5)
        gps.setdefault(code, (la, lo))
        p = pref.get(code[:3])
        if p and code not in ("75056","69123","13055"): arr[p].append((la, lo))
    for c, pts in arr.items():
        if pts and c not in gps:
            gps[c] = (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    return gps
