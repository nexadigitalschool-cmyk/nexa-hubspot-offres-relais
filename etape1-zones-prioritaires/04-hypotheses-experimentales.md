# 04 — Hypothèses expérimentales et plan d'apprentissage

L'objectif de l'année 1 est double : **générer des inscriptions** et **apprendre du marché**. Ce
document décrit ce que la sélection de zones rend testable, et comment.

**Principe directeur :** aucune des variables ci-dessous n'entre dans le score. Elles sont collectées
séparément pour pouvoir être **confrontées aux résultats commerciaux réels** en fin de saison. Les
intégrer maintenant reviendrait à sélectionner les territoires qui confirment nos hypothèses de
départ — et à ne rien apprendre.

---

## La grande hypothèse : faible offre supérieure numérique locale → meilleur potentiel À distance ?

> *Les territoires disposant d'un vivier compatible NEXA mais de peu de formations supérieures
> numériques accessibles localement présentent-ils un potentiel particulièrement important pour
> NEXA À distance ?*

**Cette étape ne cherche pas à confirmer cette hypothèse. Elle cherche à la rendre vérifiable.**

Pour cela il faut comparer, **à vivier comparable**, des zones à faible et à forte offre numérique
locale. Les paires suivantes sont constituées à cet effet :

| Forte offre supérieure locale | Faible offre supérieure locale | Écart de vivier | Coût des deux côtés |
|---|---|---|---|
| **Amiens** (~3 780, pôle sur place, **98 km de Lille**) | **Dunkerque–Calais** (~3 840, pôle à 69 km, **71 km de Lille**) | **1,6 %** | ★★★ les deux depuis Lille |
| **Le Havre** (~4 310, pôle sur place, 176 km de Paris) | **Valence** (~4 340, pôle à 70 km, **93 km de Lyon**) | **0,7 %** | ★★ deux bases différentes |
| **Besançon** (~3 030, pôle sur place, 190 km de Lyon) | **Évreux** (~3 040, pôle à 47 km, **91 km de Paris**) | **0,3 %** | ★★ deux bases différentes |
| **Lorient** (~2 960, pôle sur place, 442 km) | **Saint-Brieuc** (~2 970, pôle à 92 km, 378 km) | 0,3 % | ✗ très coûteux |
| **Chambéry** (~3 970, pôle sur place, 87 km de Lyon) | **Bayonne** (~3 930, pôle à 91 km, 558 km) | 1,0 % | ✗ asymétrique |

**La paire Amiens / Dunkerque–Calais est de très loin la meilleure** : viviers estimés identiques à
1,6 % près, offre supérieure locale radicalement opposée, et **les deux zones sont desservies par la
même base — Lille, à moins de 100 km**. C'est une expérience naturelle quasi parfaite, réalisable
pour le coût d'une seule zone lointaine.

Les paires **Le Havre / Valence** et **Besançon / Évreux** sont aussi propres statistiquement, mais
mobilisent deux bases différentes.

**Condition de validité — importante.** Ces paires reposent sur le vivier **proxy**. Elles devront
être **revalidées avec les effectifs DEPP réels** avant d'en tirer la moindre conclusion : un écart
de 2 % sur un proxy ne garantit pas un écart de 2 % sur les effectifs observés.

**Ce qui manque encore, et qui doit être collecté avant le lancement :** le nombre réel de formations
numériques post-bac (BTS SIO, BTS CIEL, BUT informatique, BUT MMI, BUT réseaux, bachelors, écoles
privées) accessibles dans chaque bassin. Cette variable **n'a pas pu être collectée** (accès Parcoursup
et ONISEP bloqué). Sans elle, « offre locale » reste approximée par la seule présence d'un pôle
étudiant majeur — une approximation grossière.

---

## Les huit hypothèses et leur terrain de test

### H1 — Les zones faiblement couvertes en formations numériques convertissent mieux

**Terrain** : les paires ci-dessus. **Zones porteuses activables à coût raisonnable** :
Dunkerque–Calais (71 km de Lille), Valence (93 km de Lyon), Évreux (91 km de Paris),
Saint-Quentin (85 km de Lille), Montélimar (134 km de Lyon).
**Zones porteuses mais coûteuses** : Vannes, Bayonne, Niort, Béziers, Saint-Brieuc, Quimper.
**Contre-terrain indispensable** : Grenoble et Rouen — offre locale forte, et tous deux proches d'une
base. Si NEXA y convertit aussi bien, H1 est fausse ou secondaire.
**Mesure** : taux leads / lycéens exposés, puis taux candidatures / leads, par zone.

### H2 — L'éloignement des grands pôles étudiants augmente l'intérêt pour le campus À distance

**Variable** : `d_pole_etudiant_km` (observée, dans `data/bassins_scores.csv`).
**Gradient disponible dans le panel** : 0 km (Rouen, Dijon, Caen, Grenoble) → 38 km (Belfort)
→ 47 km (Vannes, Évreux) → 57 km (Saint-Quentin) → 59 km (Béziers) → 69 km (Dunkerque)
→ 70 km (Valence) → 89–92 km (Angoulême, Bayonne, Saint-Brieuc) → 1 415 km (Mayotte) → La Réunion.
**Test le plus fort** : La Réunion (~7 120 Tle, aucune alternative métropolitaine). Si H2 est vraie,
ce territoire doit surperformer nettement — mais il ne peut être testé qu'à distance (9 000 km).
**Test le plus économique** : Valence et Dunkerque, tous deux à moins de 95 km d'une base.

### H3 — Un environnement économique numérique dynamique augmente l'intérêt pour les formations NEXA

**Gradient** : Marseille / Toulouse / Bordeaux / Nantes / Rennes / Grenoble / Nice (5/5) →
Rouen / Valence / Dijon / Dunkerque (3/5) → Béziers / Forbach / Saint-Quentin / Mamoudzou (1/5).
**Test décisif** : **Saint-Quentin** (économie numérique 1/5, 85 km de Lille) ou **Béziers** (1/5,
vivier ~4 410, mais 297 km). Si l'une des deux performe, **l'axe économie numérique doit être
fortement dépondéré dans le modèle de l'année 2.**
Saint-Quentin est le contre-test le moins cher, mais son vivier (~2 650 Tle) est faible : un
résultat nul y sera ambigu. Béziers offre un vivier 66 % supérieur pour un déplacement bien plus
lourd. **Dunkerque–Calais est le compromis retenu** : économie 3/5 mais en réindustrialisation
active, vivier ~3 840, et 71 km de Lille.

### H4 — L'économie numérique influence davantage l'alternance que le recrutement étudiant

**Mesure** : suivre séparément, par zone, le taux d'inscription B1 **et** le taux de signature en
alternance.
**Zones les plus informatives** : Rouen (112 km de Paris), Dunkerque–Calais (71 km de Lille),
Le Havre, Belfort–Montbéliard, Saint-Nazaire — besoins IT industriels réels, écosystème start-up
modeste — opposées à Grenoble, Rennes et Marseille.
Si H4 est vraie, l'économie numérique doit sortir du score de **recrutement** et alimenter un score
de **placement** distinct.

### H5 — Les territoires concentrant NSI / STI2D / CIEL surperforment en Cyber/Dev

**⚠️ Non testable en l'état.** Cette hypothèse porte sur des effectifs de spécialités qui **n'ont pas
pu être collectés**. Les notes cyber/dev du livrable sont des estimations issues du tissu économique,
pas des comptages d'élèves — les utiliser pour tester H5 reviendrait à tester une hypothèse contre
elle-même.
**Prérequis absolu** : lancer `pipeline/05_enrichissement_depp.py`.
**Zones porteuses une fois les données obtenues** : Rennes, Grenoble, Toulouse, Marseille, Belfort,
Vannes, Brest, Toulon.

### H6 — Les territoires à forte présence STMG ou généraliste performent en Marketing Digital

**Zones porteuses** : Bordeaux (5/5 marketing) et Nantes (5/5) sur gros vivier ; Bayonne (5/5),
Angoulême (5/5), Perpignan, Béziers, Avignon, Reims, Tours, Orléans sur vivier moyen.
**Même réserve que H5** : la présence effective de STMG doit être vérifiée sur données DEPP. Le
raisonnement actuel infère le vivier STMG depuis l'économie tertiaire locale — c'est plausible, ce
n'est pas mesuré.

### H7 — Les villes moyennes constituent un marché particulièrement intéressant

**Terrain constitué exprès** : cinq bassins ont été ajoutés sous le seuil de population pour rendre
cette hypothèse testable — **Troyes, Angoulême, Niort, Albi, Saint-Malo**. Sans eux, l'échantillon
n'aurait contenu que des agglomérations et H7 aurait été invérifiable.
**Comparaison** : ces cinq zones + Angers (ville moyenne « haut de gamme ») contre les métropoles P1.
**Zone retenue au portefeuille** : **Troyes**, seule des cinq à être proche d'une base (141 km de
Paris) — Niort est à 354 km, Angoulême à 364 km, Albi à 447 km.
**Indicateur clé** : rendement par IE (leads obtenus / IE réalisée), pas volume absolu. Une ville
moyenne ne gagnera jamais en volume ; la question est de savoir si elle gagne **au coût d'IE**.

### H8 — Les territoires disposant d'un Campus connecté présentent une meilleure réceptivité

**⚠️ Non testable en l'état.** La liste des **89 lieux labellisés Campus connecté** n'a pas pu être
récupérée (accès `enseignementsup-recherche.gouv.fr` et DGESIP bloqué). Deux implantations seulement
sont confirmées par recherche documentaire — **Cahors** et **Nevers**, parmi les 13 sites de la vague
expérimentale 2019 — et aucune ne tombe dans un bassin retenu.
**Action requise** : récupérer la liste sur `services.dgesip.fr/CampusConnectes/`, géocoder, et
croiser avec les 59 bassins. C'est une collecte de quelques heures, à faire avant le lancement.
Un Campus connecté est un **partenaire opérationnel potentiel** autant qu'une variable d'étude :
c'est un lieu qui accueille déjà des étudiants inscrits à distance.

---

## Variables expérimentales collectées ou à collecter

| Variable | Statut | Source |
|---|---|---|
| Distance au pôle étudiant majeur | **collectée** | calcul, `data/bassins_scores.csv` |
| Présence d'un pôle étudiant dans le bassin | **collectée** | calcul |
| Distance au campus NEXA le plus proche | **collectée** | calcul |
| Concentration à 20 km, étendue du bassin | **collectée** | calcul |
| Profil urbain (nb communes, nb villes ≥ 10 000) | **collectée** | INSEE/Etalab |
| Densité de population du bassin | dérivable | INSEE/Etalab |
| **Nombre de formations numériques post-bac locales** | **À COLLECTER** | Parcoursup, ONISEP |
| **BTS SIO / CIEL, BUT informatique / MMI / R&T** | **À COLLECTER** | Parcoursup |
| **Présence d'un Campus connecté** | **À COLLECTER** | DGESIP |
| **IPS moyen des lycées du bassin** | **À COLLECTER** | `fr-en-ips-lycees` |
| **Effectifs Terminale réels (GT + pro)** | **À COLLECTER** | DEPP |
| **Effectifs NSI / STI2D / CIEL / STMG** | **À COLLECTER** | DEPP |

---

## Ce qu'il faut mesurer pendant la saison pour que tout ceci serve

Sans instrumentation du funnel **par zone**, aucune de ces hypothèses ne sera vérifiable en fin
d'année. Le minimum à tracer, bassin par bassin :

```
zone → lycées prospectés → IE obtenues → lycéens exposés → leads
     → candidatures → admissions → inscriptions B1 À distance
```

Trois ratios suffisent à trancher la plupart des hypothèses :

1. **taux d'obtention d'IE** = IE obtenues / lycées prospectés → mesure l'accessibilité commerciale
   du territoire, pas son potentiel ;
2. **taux de captation** = leads / lycéens exposés → mesure l'attractivité réelle de l'offre À
   distance sur ce vivier. **C'est l'indicateur central pour H1, H2, H3 et H8** ;
3. **rendement par IE** = inscriptions / IE réalisée → l'indicateur de décision économique, et le
   seul qui permette de comparer une ville moyenne à une métropole (H7).

**Recommandation d'instrumentation** : ces trois ratios doivent être disponibles **par bassin** dans
le CRM dès la première IE. Un champ « bassin d'opportunité » sur l'objet lycée, alimenté depuis le
fichier `data/handoff_etape2.json`, suffit. Sans lui, l'année 1 produira des inscriptions mais
**aucun modèle exploitable pour l'année 2** — ce qui est précisément le risque que cette démarche
cherche à écarter.
