# Étape 1 — Où NEXA À distance doit-il tester ses Interventions Extérieures ?

**Livrable territorial. Aucune liste de lycées n'est produite ici** (c'est l'objet de l'étape 2).

Date de production : **15 août 2026** · Périmètre : France entière (métropole + DROM)
Campus physiques NEXA retenus : **Paris, Lyon, Lille** (confirmé par NEXA).

---

## Ce que contient ce dossier

| Fichier | Contenu |
|---|---|
| [`01-methodologie.md`](01-methodologie.md) | Méthode réellement appliquée, exclusion des 60 km, construction des bassins, scoring |
| [`02-bassins-candidats.md`](02-bassins-candidats.md) | Les **59 bassins d'opportunité** avec tous leurs indicateurs + classement P1/P2/P3-TEST |
| [`03-fiches-P1.md`](03-fiches-P1.md) | Lecture stratégique détaillée des **12 zones P1** |
| [`04-hypotheses-experimentales.md`](04-hypotheses-experimentales.md) | Les 8 hypothèses H1–H8, comment la sélection permet de les tester, plan d'apprentissage |
| [`05-limites-et-sources.md`](05-limites-et-sources.md) | **Ce que les données ne permettent pas encore d'affirmer**, sources et millésimes |
| [`06-handoff-etape2.md`](06-handoff-etape2.md) | Ce que l'étape 2 reçoit, bassin par bassin |
| `data/` | Résultats exploitables : CSV, JSON, périmètre d'exclusion par département |
| `pipeline/` | Scripts reproductibles (référentiels → bassins → scoring → livrables) |

---

## Deux avertissements à lire avant tout le reste

### 1. L'axe « affinité filières » n'est pas une donnée DEPP

L'environnement de production bloquait tout accès réseau à `data.education.gouv.fr`. Les effectifs
réels par établissement, par série et par spécialité (NSI, STI2D, CIEL, STMG) **n'ont pas pu être
téléchargés**. En conséquence :

- le **vivier B1** est un **PROXY** (population INSEE × ratio national Terminale de 1,05 %) ;
- les **potentiels par filière** sont des **ESTIMATIONS EXPERTES** fondées sur le tissu économique
  documenté de chaque territoire, **pas** sur des effectifs scolaires.

Ces colonnes sont signalées comme telles partout dans le livrable. Le script
[`pipeline/05_enrichissement_depp.py`](pipeline/05_enrichissement_depp.py) est fourni pour les
remplacer par les données observées dès qu'il est lancé depuis un poste au réseau ouvert.
**C'est la première action à mener avant d'engager le budget de déplacement.**

### 2. Le score ne mesure pas la « propension au distanciel »

Conformément à la consigne, aucun bonus/malus lié à l'éloignement, à la ruralité, à l'IPS, aux Campus
connectés ou à la densité d'enseignement supérieur n'entre dans le score. Ces variables sont
**collectées à part** comme variables expérimentales.

Conséquence assumée et importante : **les 12 zones P1 contiennent toutes un pôle étudiant majeur.**
Le score, en ne récompensant que le vivier, l'affinité, la concentration et l'économie numérique,
sélectionne mécaniquement des territoires bien dotés. C'est précisément pourquoi le portefeuille de
test recommandé ci-dessous ne se limite pas aux P1.

---

## Les chiffres clés

| Indicateur | Valeur | Nature |
|---|---|---|
| Communes analysées | 34 863 (68,3 M hab.) | observé — INSEE/Etalab |
| Communes exclues (≤ 60 km de Paris, Lyon ou Lille) | **2 982** — 19,1 M hab. (**28,0 %** de la population) | calculé |
| Départements totalement exclus | 4 (75, 92, 93, 94) | calculé |
| Départements partiellement touchés **et restant exploitables** | 11 | calculé |
| Bassins d'opportunité construits | 75 (dont **59 retenus et scorés**) | calculé |
| Répartition | **12 P1 · 18 P2 · 29 P3/TEST** | calculé |

Aucun département n'a été exclu en bloc : le calcul est fait commune par commune. L'Isère reste
exploitable à 59 % (Grenoble est à 94 km de Lyon), le Pas-de-Calais à 54 %, l'Oise à 64 %.

**Sortent en revanche du champ** : Saint-Étienne (≈ 51 km de Lyon), Valenciennes, Arras, Douai,
Béthune (< 60 km de Lille), Beauvais, Creil, Compiègne et Melun (< 60 km de Paris). Ce sont des
« villes moyennes » souvent citées spontanément — la règle des 60 km les neutralise.

---

## Le classement, en une ligne

**P1 (12)** — Marseille · Toulouse · Bordeaux · Nantes · Nice · Rennes · Grenoble · Strasbourg ·
Montpellier–Nîmes · Angers · Rouen · Clermont-Ferrand

**P2 (18)** — Annecy · Toulon · Brest · Tours · La Réunion · Pau · Vannes · Orléans · Mulhouse ·
Metz · Caen · Dijon · Bayonne · Nancy · Niort · Avignon · Belfort–Montbéliard · Le Havre

**P3/TEST (29)** — dont Le Mans, Valence, Lorient, Chambéry, Poitiers, Besançon, La Rochelle, Troyes,
Perpignan, Saint-Nazaire, Amiens, Angoulême, Dunkerque–Calais, Béziers…

---

## La tension centrale : les meilleures zones sont loin de vos trois campus

Avec Paris, Lyon et Lille pour seules bases de tournée, les quatre meilleurs bassins après Marseille
sont **Toulouse (361 km), Bordeaux (434 km), Nantes (343 km) et Nice (296 km)**. Aucun n'est
activable en aller-retour dans la journée.

À l'inverse, les zones proches d'une base sont d'un cran en dessous au score, mais restent solides :
Grenoble (94 km de Lyon), Annecy (101), Rouen (112 de Paris), Orléans (115), Clermont-Ferrand (133),
Valence (93), Chambéry (87), Amiens (98 de Lille), Dunkerque (71), Troyes (141), Reims (129).

**Il faut donc arbitrer explicitement entre score et coût.** Le portefeuille ci-dessous assume
**un seul long-courrier** — Marseille, parce que c'est le premier vivier de France hors exclusion —
et optimise le reste sur le coût d'accès.

---

## Recommandation finale : tester 8 bassins, pas 59

Avec une petite équipe et un budget de déplacement limité, la contrainte réelle n'est pas le nombre
de zones intéressantes — il y en a beaucoup — mais **le nombre d'IE nécessaires pour qu'une zone
produise un signal lisible**. En dessous de 3 à 5 IE dans un bassin, un résultat nul ne se distingue
pas du bruit : on ne saura pas si la zone est mauvaise ou si elle a été mal travaillée.

Sur une saison d'IE (octobre → mars, ~20 semaines utiles), un objectif réaliste est de **8 bassins ×
4 à 5 IE ≈ 35 IE**. Au-delà, NEXA disperse son budget et **n'apprend rien** — ce qui est le vrai coût.

| Rôle | Bassin | Prio | Base | Distance | Ce qu'on va apprendre |
|---|---|---|---|---|---|
| **Cœur de cible** | **Marseille – Aix** | P1 (1er) | Lyon | 277 km | Le plus gros vivier de France hors exclusion (~18 520 Tle) : le plafond de ce qu'une zone peut produire |
| **Cœur de cible** | **Grenoble** | P1 (7e) | Lyon | 94 km | Vivier scientifique maximal, bassin le plus concentré du panel (88/100) |
| **Cœur de cible** | **Rouen** | P1 (11e) | Paris | 112 km | Meilleur rapport vivier / coût de déplacement de tout l'univers (~8 080 Tle) |
| **Cœur de cible** | **Clermont-Ferrand** | P1 (12e) | Lyon | 133 km | Capitale régionale isolée, sans métropole concurrente à moins de 2 h |
| **Cœur de cible** | **Orléans** | P2 (20e) | Paris | 115 km | Meilleure concentration du panel (89/100) : 4–5 IE réalisables en deux jours |
| **Adjacente** | **Valence** | P3 (32e) | Lyon | 93 km | Vivier réel (~4 340 Tle) **sans** pôle étudiant à moins de 70 km : **test direct de H1 et H2** |
| **Adjacente** | **Troyes** | P3 (38e) | Paris | 141 km | Ville moyenne dotée d'une université de technologie : **test de H7** |
| **Expérimentale** | **Dunkerque – Calais** | P3 (45e) | Lille | 71 km | Vivier ~3 840 Tle, aucun pôle étudiant à 69 km, réindustrialisation en cours : **contre-test H1 + H3 + H4** |

Sept des huit zones sont à moins de 145 km d'une base. **Le budget déplacement se concentre sur une
seule zone longue distance.**

### Le neuvième bassin, s'il y a du budget : Amiens

Amiens est à **98 km de Lille**, comme Dunkerque (71 km) — et leurs viviers estimés sont
**identiques à 1,6 % près** (~3 780 contre ~3 840 Terminales). Mais Amiens **possède** une université
de plein exercice quand Dunkerque n'en a aucune à moins de 69 km.

C'est une **expérience naturelle quasi parfaite**, sur deux zones desservies par la même base, à coût
marginal. Si une seule chose devait être ajoutée au plan, c'est celle-là : elle transforme un
contre-test isolé en comparaison interprétable.

### Si le budget ne permet que 5 bassins

**Rouen, Grenoble, Orléans, Valence, Dunkerque.** On conserve l'opposition centrale forte offre
locale / faible offre locale (Rouen–Grenoble–Orléans contre Valence–Dunkerque), qui est
l'apprentissage le plus rentable, pour un coût de déplacement minimal — aucune zone à plus de 135 km.

On renonce alors à Marseille, donc à la mesure du plafond national. C'est un arbitrage défendable
en année 1 : mieux vaut un apprentissage propre qu'un gros chiffre isolé.

---

## Reproduire l'analyse

```bash
cd pipeline
python3 01_telechargement_referentiels.py   # référentiels INSEE/Etalab + La Poste
python3 02_bassins.py                        # exclusion 60 km + construction des bassins
python3 03_scoring.py                        # score d'opportunité territoriale
python3 04_exclusion_export.py               # périmètre d'exclusion par département
python3 06_livrables.py                      # tableau de synthèse + handoff étape 2

python3 05_enrichissement_depp.py --inspect  # À LANCER : remplace les proxys par les données DEPP
```
