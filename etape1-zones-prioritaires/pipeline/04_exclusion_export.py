import json, csv, math
import numpy as np
from gpsfix import build_gps
R=6371.0088
CAMPUS_A={"Paris":(48.8709,2.3646),"Lyon":(45.7578,4.8320),"Lille":(50.6216,3.0790)}
CAMPUS_B=dict(CAMPUS_A,**{"Bordeaux":(44.8672,-0.5560),"Nantes":(47.2043,-1.5535),"Marseille":(43.2555,5.3980)})
deps_nom={d["code"]:d["nom"] for d in json.load(open("deco/package/data/departements.json"))}
gps=build_gps()
C=[c for c in json.load(open("deco/package/data/communes.json"))
   if c.get("type")=="commune-actuelle" and c.get("population") and gps.get(c["code"])]
lats=np.array([gps[c["code"]][0] for c in C]); lons=np.array([gps[c["code"]][1] for c in C])
pops=np.array([c["population"] for c in C],float); deps=[c["departement"] for c in C]
rlat=np.radians(lats)
def d_all(p):
    p2=math.radians(p[0])
    h=np.sin((p2-rlat)/2)**2+np.cos(rlat)*math.cos(p2)*np.sin(np.radians(p[1]-lons)/2)**2
    return 2*R*np.arcsin(np.sqrt(h))
dA=np.min(np.vstack([d_all(v) for v in CAMPUS_A.values()]),axis=0)
dB=np.min(np.vstack([d_all(v) for v in CAMPUS_B.values()]),axis=0)
eA,eB=dA<=60,dB<=60
agg={}
for i,c in enumerate(C):
    d=deps[i]; a=agg.setdefault(d,[0,0,0,0.0,0.0,0.0])
    a[0]+=1; a[3]+=pops[i]
    if eA[i]: a[1]+=1; a[4]+=pops[i]
    if eB[i]: a[2]+=1; a[5]+=pops[i]
rows=[]
for d,a in sorted(agg.items()):
    if a[1]==0 and a[2]==0: continue
    rows.append([d,deps_nom.get(d,""),a[0],a[1],round(100*a[1]/a[0],1),int(a[3]),int(a[4]),
                 round(100*a[4]/a[3],1),a[2],round(100*a[2]/a[0],1),
                 "totalement exclu" if a[1]/a[0]>=0.995 else ("majoritairement exclu" if a[1]/a[0]>=0.5 else "partiellement exclu - reste exploitable")])
with open("exclusion_departements.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f,delimiter=";")
    w.writerow(["dep","departement","nb_communes","communes_exclues_A","pct_communes_exclues_A",
                "population_totale","population_exclue_A","pct_population_exclue_A",
                "communes_exclues_B","pct_communes_exclues_B","statut_perimetre_A"])
    w.writerows(rows)
print(f"{'dep':<4}{'nom':<26}{'%comm A':>9}{'%pop A':>8}{'%comm B':>9}  statut")
for r in rows: print(f"{r[0]:<4}{r[1][:25]:<26}{r[4]:>8.1f}%{r[7]:>7.1f}%{r[9]:>8.1f}%  {r[10]}")
print(f"\nTotal exclu A : {eA.sum()} communes / {pops[eA].sum():,.0f} hab")
print(f"Total exclu B : {eB.sum()} communes / {pops[eB].sum():,.0f} hab")
