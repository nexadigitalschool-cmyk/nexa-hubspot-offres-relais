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

## Une règle de lecture : le coût de déplacement n'entre pas dans la sélection

La distance aux campus **ne participe ni au score ni au choix des zones**. Elle est calculée et
conservée dans les données (`d_campus_nexa_km`) comme **information opérationnelle**, au même titre
que les variables expérimentales : elle sert à organiser les tournées une fois les zones choisies,
pas à décider lesquelles sont pertinentes.

La contrainte budgétaire agit donc sur **le nombre** de zones testées, pas sur **lesquelles**.

---

## Recommandation finale : tester 9 bassins, pas 59

Avec une petite équipe, la contrainte réelle est **le nombre d'IE nécessaires pour qu'une zone
produise un signal lisible**. En dessous de 3 à 5 IE dans un bassin, un résultat nul ne se distingue
pas du bruit : on ne saura pas si la zone est mauvaise ou si elle a été mal travaillée.

Sur une saison d'IE (octobre → mars, ~20 semaines utiles), un objectif réaliste est de **9 bassins ×
4 à 5 IE ≈ 40 IE**. Au-delà, NEXA disperse son effort et **n'apprend rien** — ce qui est le vrai coût.

La sélection applique la logique **70 / 20 / 10** et veille à ce que le cœur de cible ne soit pas
composé de six territoires au même profil.

### Cœur de cible — 6 zones (67 %)

Les fondamentaux mesurables les plus solides, choisis pour **couvrir des profils de filières
différents** :

| Bassin | Rang | Vivier (Tle est.) | Profil dominant | Ce qu'il apporte au panel |
|---|---|---|---|---|
| **Marseille – Aix** | 1 | ~18 520 | Cyber + Dev + Data/IA | Le plus gros vivier de France hors exclusion : mesure le plafond |
| **Toulouse** | 2 | ~13 900 | Cyber + Dev + Data/IA | Affinité maximale (94/100) **et** forte concentration (81/100) |
| **Bordeaux** | 3 | ~12 650 | **Dev + Marketing** | Le seul gros vivier du cœur orienté marketing (Cdiscount, Ubisoft, vin, tourisme) |
| **Rennes** | 6 | ~7 500 | **Cyber pur** | Pôle cyber national, bassin le plus compact du top 10 (87/100) |
| **Grenoble** | 7 | ~7 210 | Cyber + Dev + **Data/IA**, marketing faible | Territoire délibérément **spécialisé** : teste l'offre technique isolément |
| **Rouen** | 11 | ~8 080 | **Cyber industriel** | Seul profil non-« French Tech » du cœur (économie 3/5) : teste H4 |

**Nantes (4ᵉ) et Nice (5ᵉ) sont volontairement écartés du premier lot** — non par manque de
potentiel, mais parce que leurs profils recoupent presque exactement ceux de Bordeaux et de Toulouse.
Ce sont les **deux premières réserves** : à substituer immédiatement si une zone du cœur se révèle
inexploitable.

### Cibles adjacentes — 2 zones (22 %)

Potentiel sérieux, **configuration franchement différente** :

| Bassin | Rang | Vivier | Pourquoi elle est là |
|---|---|---|---|
| **Niort** | 27 | ~2 390 | **L'anomalie la plus forte du panel** : affinité 88/100 pour un vivier indexé à 1/100. MAIF, MACIF, MAAF, Groupama. Teste directement : **l'affinité compense-t-elle le volume ?** |
| **Vannes** | 19 | ~3 460 | Pôle cyber breton **sans université de plein exercice** (pôle étudiant à 47 km). Teste H1 et H2 sur un profil spécialisé, à opposer à Rennes |

### Zone expérimentale — 1 zone (11 %)

| Bassin | Rang | Vivier | Pourquoi elle est là |
|---|---|---|---|
| **Béziers – Narbonne** | 55 | ~4 410 | **Le contre-test le plus pur.** Vivier réel — supérieur à celui de Niort et de Vannes — mais économie numérique notée **1/5** et aucun pôle étudiant à moins de 59 km. Si Béziers convertit, l'axe économie numérique doit être fortement dépondéré en année 2 |

### Le cas à part : La Réunion

La Réunion (17ᵉ, ~7 120 Terminales estimées) est **le test le plus discriminant de H2** — éloignement
maximal de toute alternative métropolitaine. Elle n'est pas dans les 9 non pour son potentiel, mais
parce qu'elle appelle une **modalité de test différente** : webinaires, partenariats rectorat et
lycées, relais locaux, plutôt que des IE en présentiel. À lancer en parallèle, sur un budget distinct.

### Si la capacité ne permet que 5 bassins

**Marseille, Toulouse, Rennes, Niort, Béziers.** On garde les deux plus gros viviers, un profil cyber
très concentré, l'anomalie d'affinité et le contre-test — c'est-à-dire l'essentiel du pouvoir
d'apprentissage du panel complet.

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
