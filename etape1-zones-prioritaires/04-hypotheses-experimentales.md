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

| Vivier estimé | Forte offre supérieure locale | Faible offre supérieure locale | Écart de vivier |
|---|---|---|---|
| ~3 500–4 000 Tle | **Chambéry** (~3 970, pôle étudiant sur place) | **Vannes** (~3 460, pôle à 47 km) | 13 % |
| ~4 000–4 600 Tle | **Le Havre** (~4 310, pôle sur place) | **Béziers–Narbonne** (~4 410, pôle à 59 km) | 2 % |
| ~3 000–3 200 Tle | **Besançon** (~3 030, pôle sur place) | **Saint-Brieuc** (~2 970, pôle à 92 km) | 2 % |
| ~2 400 Tle | **Poitiers** (~3 210, pôle sur place) | **Angoulême** (~2 390, pôle à 89 km) | 34 % |
| ~3 700–4 300 Tle | **Le Mans** (~4 230, pôle sur place) | **Belfort–Montbéliard** (~3 700, pôle à 38 km) | 14 % |

Les paires **Le Havre / Béziers** et **Besançon / Saint-Brieuc** sont les plus propres : moins de 3 %
d'écart de vivier estimé, et une opposition nette sur l'offre locale.

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

**Terrain** : les paires ci-dessus. **Zones porteuses** : Vannes, Béziers, Saint-Brieuc, Angoulême,
Quimper, Saint-Malo, Dunkerque.
**Contre-terrain indispensable** : Rennes et Grenoble — offre locale maximale. Si NEXA y convertit
aussi bien, H1 est fausse ou secondaire.
**Mesure** : taux leads / lycéens exposés, puis taux candidatures / leads, par zone.

### H2 — L'éloignement des grands pôles étudiants augmente l'intérêt pour le campus À distance

**Variable** : `d_pole_etudiant_km` (observée, dans `data/bassins_scores.csv`).
**Gradient disponible dans le panel** : 0 km (Rouen, Dijon, Caen) → 38 km (Belfort) → 47 km (Vannes)
→ 59 km (Béziers) → 69 km (Dunkerque) → 91 km (Bayonne) → 92 km (Saint-Brieuc) → 1 415 km (Mayotte)
→ La Réunion.
**Test le plus fort** : La Réunion. Si H2 est vraie, ce territoire doit surperformer nettement.

### H3 — Un environnement économique numérique dynamique augmente l'intérêt pour les formations NEXA

**Gradient** : Toulouse / Rennes / Grenoble / Nice (5/5) → Rouen / Valence / Dijon (3/5) →
Béziers / Forbach / Saint-Quentin / Mamoudzou (1/5).
**Test décisif** : Béziers. Vivier réel, économie numérique notée 1/5. **Si Béziers performe, l'axe
économie numérique doit être fortement dépondéré dans le modèle de l'année 2.**

### H4 — L'économie numérique influence davantage l'alternance que le recrutement étudiant

**Mesure** : suivre séparément, par zone, le taux d'inscription B1 **et** le taux de signature en
alternance.
**Zones les plus informatives** : Rouen, Le Havre, Belfort–Montbéliard, Dunkerque (besoins IT réels,
écosystème start-up modeste) opposées à Rennes et Grenoble.
Si H4 est vraie, l'économie numérique doit sortir du score de **recrutement** et alimenter un score
de **placement** distinct.

### H5 — Les territoires concentrant NSI / STI2D / CIEL surperforment en Cyber/Dev

**⚠️ Non testable en l'état.** Cette hypothèse porte sur des effectifs de spécialités qui **n'ont pas
pu être collectés**. Les notes cyber/dev du livrable sont des estimations issues du tissu économique,
pas des comptages d'élèves — les utiliser pour tester H5 reviendrait à tester une hypothèse contre
elle-même.
**Prérequis absolu** : lancer `pipeline/05_enrichissement_depp.py`.
**Zones porteuses une fois les données obtenues** : Rennes, Grenoble, Toulouse, Belfort, Vannes, Brest.

### H6 — Les territoires à forte présence STMG ou généraliste performent en Marketing Digital

**Zones porteuses** : Bayonne (5/5 marketing), Angoulême (5/5), Perpignan, Béziers, Avignon, Reims,
Tours, Orléans.
**Même réserve que H5** : la présence effective de STMG doit être vérifiée sur données DEPP. Le
raisonnement actuel infère le vivier STMG depuis l'économie tertiaire locale — c'est plausible, ce
n'est pas mesuré.

### H7 — Les villes moyennes constituent un marché particulièrement intéressant

**Terrain constitué exprès** : quatre bassins ont été ajoutés sous le seuil de population pour rendre
cette hypothèse testable — **Troyes, Angoulême, Niort, Albi**. Sans eux, l'échantillon n'aurait
contenu que des agglomérations et H7 aurait été invérifiable.
**Comparaison** : ces quatre zones + Angers (ville moyenne « haut de gamme ») contre les métropoles P1.
**Indicateur clé** : rendement par IE (leads obtenus / IE réalisée), pas volume absolu. Une ville
moyenne ne gagnera jamais en volume ; la question est de savoir si elle gagne **au coût d'IE**.

### H8 — Les territoires disposant d'un Campus connecté présentent une meilleure réceptivité

**⚠️ Non testable en l'état.** La liste des **89 lieux labellisés Campus connecté** n'a pas pu être
récupérée (accès `enseignementsup-recherche.gouv.fr` et DGESIP bloqué). Deux implantations seulement
sont confirmées par recherche documentaire — **Cahors** et **Nevers**, parmi les 13 sites de la vague
expérimentale 2019 — et aucune ne tombe dans un bassin retenu.
**Action requise** : récupérer la liste sur `services.dgesip.fr/CampusConnectes/`, géocoder, et
croiser avec les 53 bassins. C'est une collecte de quelques heures, à faire avant le lancement.
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
