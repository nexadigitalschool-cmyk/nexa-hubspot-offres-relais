# Étape 1 — Où NEXA À distance doit-il tester ses Interventions Extérieures ?

**Livrable territorial. Aucune liste de lycées n'est produite ici** (c'est l'objet de l'étape 2).

Date de production : **15 août 2026** · Périmètre : France entière (métropole + DROM)

---

## Ce que contient ce dossier

| Fichier | Contenu |
|---|---|
| [`01-methodologie.md`](01-methodologie.md) | Méthode réellement appliquée, exclusion des 60 km, construction des bassins, scoring |
| [`02-bassins-candidats.md`](02-bassins-candidats.md) | Les **53 bassins d'opportunité** avec tous leurs indicateurs + classement P1/P2/P3-TEST |
| [`03-fiches-P1.md`](03-fiches-P1.md) | Lecture stratégique détaillée des **12 zones P1** |
| [`04-hypotheses-experimentales.md`](04-hypotheses-experimentales.md) | Les 8 hypothèses H1–H8, comment la sélection permet de les tester, plan d'apprentissage |
| [`05-limites-et-sources.md`](05-limites-et-sources.md) | **Ce que les données ne permettent pas encore d'affirmer**, sources et millésimes |
| [`06-handoff-etape2.md`](06-handoff-etape2.md) | Ce que l'étape 2 reçoit, bassin par bassin |
| `data/` | Résultats exploitables : CSV, JSON, périmètre d'exclusion par département |
| `pipeline/` | Scripts reproductibles (référentiels → bassins → scoring → livrables) |

---

## Trois avertissements à lire avant tout le reste

### 1. NEXA a six campus, pas trois

La mission demandait d'exclure les zones situées à ≤ 60 km de **Paris, Lyon et Lille**. La recherche
documentaire montre que NEXA Digital School opère en réalité **six campus physiques** : Paris, Lyon,
Lille, **Bordeaux, Nantes et Marseille** ([nexa.fr/ecole](https://www.nexa.fr/ecole), consulté le 15/08/2026).

La règle demandée a été appliquée telle quelle (**périmètre A**), mais un **périmètre B** a été calculé
en parallèle. Huit bassins sont concernés — Marseille, Bordeaux, Nantes, Toulon, Saint-Nazaire, Cholet,
La Roche-sur-Yon, La Teste-de-Buch — et ont été **sortis de l'univers scoré** : y envoyer le campus À
distance reviendrait à concurrencer frontalement un campus physique NEXA, exactement ce que la règle
des 60 km cherche à éviter. **À confirmer par NEXA.**

### 2. L'axe « affinité filières » n'est pas une donnée DEPP

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

### 3. Le score ne mesure pas la « propension au distanciel »

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
| Communes exclues, périmètre A (Paris/Lyon/Lille) | **2 982** — 19,1 M hab. (28,0 %) | calculé |
| Communes exclues, périmètre B (+ Bordeaux/Nantes/Marseille) | 4 040 — 25,4 M hab. (37,2 %) | calculé |
| Bassins d'opportunité construits | 75 (dont 53 retenus et scorés) | calculé |
| Répartition | **12 P1 · 18 P2 · 23 P3/TEST** | calculé |

Aucun département n'a été exclu en bloc : le calcul est fait commune par commune. Douze départements
sont partiellement touchés et **restent exploitables** (voir `data/exclusion_departements.csv`).

---

## Recommandation finale : tester 8 bassins, pas 53

Avec une petite équipe et un budget de déplacement limité, la contrainte réelle n'est pas le nombre de
zones intéressantes — il y en a beaucoup — mais **le nombre d'IE nécessaires pour qu'une zone produise
un signal lisible**. En dessous de 3 à 5 IE dans un bassin, un résultat nul ne se distingue pas du
bruit : on ne saura pas si la zone est mauvaise ou si elle a été mal travaillée.

Sur une saison d'IE (octobre → mars, ~20 semaines utiles), un objectif réaliste est de **8 bassins ×
4 à 5 IE ≈ 35 IE**. Au-delà, NEXA disperse son budget et **n'apprend rien** — ce qui est le vrai coût.

Le portefeuille proposé applique la logique 70 / 20 / 10 **et** exploite les campus existants comme
bases de tournée, ce qui réduit fortement le coût du test :

| Rôle | Bassin | Prio | Base de tournée | Ce qu'on va apprendre |
|---|---|---|---|---|
| **Cœur de cible** | **Rennes** | P1 | Nantes (101 km) | Un vivier cyber/dev très dense convertit-il malgré une offre locale forte ? |
| **Cœur de cible** | **Grenoble** | P1 | Lyon (94 km) | Idem en contexte deeptech, vivier scientifique maximal |
| **Cœur de cible** | **Rouen** | P1 | Paris (112 km) | Gros vivier, économie industrielle, faible concurrence école numérique privée |
| **Cœur de cible** | **Angers** | P1 | Nantes (82 km) | Ville moyenne haut de gamme, tissu IoT/électronique |
| **Cœur de cible** | **Toulouse** | P1 | Bordeaux (212 km) | Le plus gros vivier hors exclusion : plafond de ce que peut produire une zone |
| **Adjacente** | **Niort** | P2 | Nantes (128 km) | Vivier faible **mais** affinité data/dev maximale (mutuelles) : l'affinité compense-t-elle le volume ? |
| **Adjacente** | **Vannes** | P2 | Nantes (104 km) | Pôle cyber sans pôle étudiant majeur (47 km) : **test direct de H1 et H2** |
| **Expérimentale** | **Béziers** | P3 | Marseille (175 km) | Vivier réel, économie numérique quasi nulle, pas de pôle étudiant (59 km) : **contre-test** |

Trois de ces bassins (Rennes, Angers, Vannes, + Niort) sont accessibles depuis **Nantes**, deux depuis
**Paris/Lyon**. Une part importante des déplacements devient donc du trajet court plutôt que de la
nuitée.

**Ce portefeuille est construit pour être lisible en fin de saison** : il oppose délibérément des zones
à forte offre supérieure locale (Rennes, Grenoble) à des zones qui en sont dépourvues (Vannes, Béziers),
à vivier partiellement comparable. C'est la condition pour que l'année 2 s'appuie sur des résultats
observés plutôt que sur les hypothèses de départ.

Si le budget ne permet que **5 bassins** : Rennes, Rouen, Angers, Vannes, Béziers — on conserve
l'opposition centrale forte offre / faible offre, qui est l'apprentissage le plus rentable.

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
