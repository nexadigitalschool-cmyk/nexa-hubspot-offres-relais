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

| Forte offre supérieure locale | Faible offre supérieure locale | Écart de vivier | Contrôle |
|---|---|---|---|
| **Lorient** (~2 960, pôle sur place) | **Saint-Brieuc** (~2 970, pôle à 92 km) | **0,3 %** | ★★★ même région (Bretagne), même façade littorale |
| **Amiens** (~3 780, pôle sur place) | **Dunkerque–Calais** (~3 840, pôle à 69 km) | **1,6 %** | ★★★ même région (Hauts-de-France), profil industriel commun |
| **La Rochelle** (~4 000, pôle sur place) | **Bayonne** (~3 930, pôle à 91 km) | **1,8 %** | ★★★ même région, économie littorale et touristique commune |
| **Besançon** (~3 030, pôle sur place) | **Évreux** (~3 040, pôle à 47 km) | 0,3 % | ★★ régions et structures différentes |
| **Le Havre** (~4 310, pôle sur place) | **Valence** (~4 340, pôle à 70 km) | 0,7 % | ★★ deux bassins industriels moyens, régions différentes |
| **Perpignan** (~4 720, pôle sur place) | **Béziers–Narbonne** (~4 410, pôle à 59 km) | 6,6 % | ★★★ même région, mêmes structures économiques — écart de vivier plus large |

**Les trois premières paires sont les plus solides** : au-delà d'un vivier estimé quasi identique,
elles apparient des territoires de **même région**, ce qui neutralise en partie les effets
académiques, culturels et socio-économiques régionaux. La paire **Lorient / Saint-Brieuc** est la
mieux contrôlée du panel.

La paire **Perpignan / Béziers** mérite une mention à part : l'écart de vivier y est plus large
(6,6 %), mais les deux bassins sont limitrophes, de même région, de même structure économique
(tourisme, viticulture, économie numérique faible) — et l'un possède une université quand l'autre en
est dépourvu. C'est le test H1 le plus « toutes choses égales par ailleurs » disponible.

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

**Terrain** : les paires ci-dessus. **Zones porteuses**, classées par taille de vivier :
Béziers–Narbonne (~4 410), Valence (~4 340), Bayonne (~3 930), Dunkerque–Calais (~3 840),
Saint-Nazaire (~3 760), Belfort–Montbéliard (~3 700), Vannes (~3 460), Quimper (~3 100),
Évreux (~3 040), Saint-Brieuc (~2 970), Colmar (~2 970), Saint-Quentin (~2 650), Niort (~2 390).
**Contre-terrain indispensable** : Rennes et Grenoble — offre supérieure locale maximale. Si NEXA y
convertit aussi bien, H1 est fausse ou secondaire.
**Zones retenues au portefeuille pour ce test** : **Vannes** (à opposer à Rennes, même filière cyber)
et **Béziers–Narbonne** (plus gros vivier du groupe).
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
**Test décisif** : **Béziers–Narbonne**, retenu au portefeuille. Économie numérique 1/5, mais un
vivier de ~4 410 Terminales estimées — 66 % de plus que Saint-Quentin, l'autre candidat à 1/5, dont
le vivier trop faible rendrait un résultat nul ininterprétable.
**Si Béziers convertit, l'axe économie numérique doit être fortement dépondéré dans le modèle de
l'année 2** — et l'hypothèse d'un potentiel porté par le seul vivier scolaire prend le dessus.

### H4 — L'économie numérique influence davantage l'alternance que le recrutement étudiant

**Mesure** : suivre séparément, par zone, le taux d'inscription B1 **et** le taux de signature en
alternance.
**Zones les plus informatives** : Rouen (retenu au portefeuille), Le Havre, Belfort–Montbéliard,
Dunkerque–Calais, Saint-Nazaire — besoins IT industriels réels, écosystème start-up modeste —
opposées à Grenoble, Rennes et Marseille.
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
**Zone retenue au portefeuille** : **Niort**, qui cumule le statut de ville moyenne et l'anomalie
d'affinité la plus forte du panel (88/100 pour un vivier indexé à 1/100). Troyes, Angoulême, Albi et
Saint-Malo restent les compléments naturels si la capacité de l'équipe augmente.
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
