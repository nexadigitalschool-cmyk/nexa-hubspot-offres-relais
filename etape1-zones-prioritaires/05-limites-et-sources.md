# 05 — Limites, données manquantes et sources

---

## 1. Ce que ce livrable ne permet pas d'affirmer

À lire avant d'engager le moindre budget.

### Le vivier n'est pas mesuré

Toutes les valeurs `tle_estim` sont issues de **population × 1,05 %**. Ce ratio est un ordre de
grandeur national. Il ignore :

- la **structure par âge locale** — La Réunion et Mayotte sont nettement plus jeunes que la moyenne :
  leur vivier est probablement **sous-estimé** ; les bassins à population vieillissante (Béziers,
  Perpignan, Saint-Malo) sont probablement **surestimés** ;
- **l'attractivité scolaire** d'une ville-centre sur sa périphérie — un lycée de centre-ville
  scolarise des élèves résidant hors du rayon de 30 km, ce que le proxy n'attribue pas au bassin ;
- le **poids de l'enseignement privé**, très variable selon les régions (fort en Bretagne et Pays de
  la Loire, faible dans le Sud-Est) ;
- les **taux de scolarisation et de redoublement** locaux.

**Conséquence pratique :** ces chiffres servent à **classer** des bassins entre eux, pas à
dimensionner une campagne. Ne pas les reprendre dans un budget ou un objectif commercial.

### L'affinité par filière n'est pas une donnée scolaire

Les notes cyber / dev / data / marketing sont dérivées du **tissu économique** de chaque territoire.
Elles reposent sur une chaîne de raisonnement plausible mais non vérifiée :

> économie industrielle locale → lycées techniques → présence de STI2D et Bac Pro CIEL → vivier cyber/dev

**Chaque maillon peut être faux.** Deux faits nationaux invitent à la prudence :

- **un lycée sur trois ne propose toujours pas la spécialité NSI** ;
- **NSI ne représente que 4,0 % des élèves de Terminale générale en 2025** (4,5 % en 2024, en baisse).

Autrement dit, le vivier « NSI » d'un bassin de 5 000 Terminales générales se compte en **quelques
centaines d'élèves**, très inégalement répartis entre établissements. Un territoire industriel peut
parfaitement n'offrir NSI que dans deux lycées.

**Conséquence pratique :** l'axe affinité (25 % du score) doit être remplacé par des données DEPP
**avant** l'allocation du budget de déplacement.

### La « propension au distanciel » n'est pas mesurée du tout

C'est un choix méthodologique délibéré, pas un oubli. Aucune donnée ne permet aujourd'hui d'affirmer
qu'un lycéen d'un territoire peu doté est plus enclin à s'inscrire dans un campus À distance. C'est
**l'objet même de l'expérimentation de l'année 1**.

### Le score est un outil de tri, pas une mesure

40 % du score repose sur un proxy, 40 % supplémentaires (25 % affinité + 15 % économie) sur du
jugement expert. Seuls 20 % (concentration) sont entièrement observés. **Les écarts de score
inférieurs à ~5 points ne sont pas significatifs** — Metz et Caen sont à 48,3 tous les deux, et
l'ordre entre les rangs 18 et 30 ne doit pas être interprété comme un classement.

### Les distances sont orthodromiques, pas routières

Toutes les distances sont calculées à vol d'oiseau. L'écart avec le temps de trajet réel est
important en zone de relief (Grenoble, Annecy, La Réunion) et sur les littoraux découpés (Bretagne,
Var). Pour la planification opérationnelle des tournées en étape 2, **recalculer en temps de trajet
routier**.

Cela vaut aussi pour l'exclusion des 60 km : une commune à 58 km à vol d'oiseau de Lyon peut être à
plus de 75 min de route. La règle a été appliquée telle qu'énoncée, mais **la frontière est poreuse**
et mérite un arbitrage NEXA sur les cas limites.

### Les bassins bicéphales

Trois bassins regroupent des marchés que l'algorithme fusionne par contiguïté mais qui doivent être
travaillés séparément : **Montpellier–Nîmes** (53 km d'étendue, 33 % de la population à 20 km),
**Annecy–Annemasse–Genevois** (55 km, 50 %), **Dunkerque–Calais** (56 km, 50 %) et
**Marseille–Aix–étang de Berre** (57 km, tricéphale).

---

## 2. Données manquantes, par ordre de priorité

| # | Donnée manquante | Impact | Source | Effort |
|---|---|---|---|---|
| 1 | **Effectifs Terminale réels par établissement** | Remplace le proxy du vivier — axe à 40 % | `fr-en-lycee_gt-effectifs-niveau-sexe-lv`, `fr-en-lycee_pro-effectifs-niveau-sexe-lv` | script fourni |
| 2 | **Effectifs par spécialité (NSI, maths) et série (STI2D, STMG, CIEL)** | Remplace l'affinité experte — axe à 25 % | `fr-en-effectifs-specialites-doublettes-terminale-generale` | script fourni |
| 3 | **Nombre de lycées par bassin** | Dimensionne la cible commerciale de l'étape 2 | `fr-en-annuaire-education` | script fourni |
| 4 | **Liste des 89 Campus connectés** | Rend H8 testable ; partenaires opérationnels potentiels | `services.dgesip.fr/CampusConnectes/` | ~2 h |
| 5 | **Offre supérieure numérique locale** (BTS SIO/CIEL, BUT info/MMI/R&T, bachelors) | Rend H1 réellement testable | Parcoursup, ONISEP | ~1 j |
| 6 | **IPS des lycées** | Variable expérimentale socio-économique | `fr-en-ips-lycees` | script fourni |
| 7 | **Emploi numérique par bassin** | Fiabilise l'axe économie (15 %) | France Travail, INSEE Flores, Numeum | ~1 j |
| 8 | **Temps de trajet routier** (à la place des distances à vol d'oiseau) | Fiabilise l'arbitrage score / coût, décisif dans le choix du portefeuille | API itinéraires | ~2 h |

Les points 1, 2, 3 et 6 sont couverts par `pipeline/05_enrichissement_depp.py`, qui n'a pas pu être
exécuté ici faute d'accès réseau.

---

## 3. Sources utilisées et millésimes

### Données structurantes (observées, intégrées au calcul)

| Source | Millésime | Usage | Accès |
|---|---|---|---|
| **INSEE / Etalab** — `@etalab/decoupage-administratif` v6.0.0 | population légale en vigueur 2026 | population, département, région, EPCI de 34 863 communes | npm, 15/08/2026 |
| **La Poste** — base officielle des codes postaux (miroir `high54/Communes-France-JSON`) | 2025 | coordonnées GPS par code INSEE | GitHub, 15/08/2026 |
| **IGN / Etalab** — `gregoiredavid/france-geojson` | 2024 | contours départementaux (contrôle) | GitHub, 15/08/2026 |

### Ancrages nationaux (publiés, utilisés pour calibrer le proxy)

| Fait | Valeur | Millésime | Source |
|---|---|---|---|
| Élèves en formations générales et technologiques (lycée) | ~1,597 M | rentrée 2024 | DEPP, RERS 2025 |
| Élèves en voie professionnelle (lycée, hors apprentis) | ~651 000 | rentrée 2024 | DEPP |
| Élèves du second degré, tous niveaux | 5,621 M | rentrée 2025 | DEPP |
| Part de NSI en Terminale générale | **4,0 %** (4,5 % en 2024) | 2025 | DEPP, note d'information Enseignements de spécialités |
| Part des filles en NSI Terminale | 13,7 % | 2024 | DEPP |
| Lycées ne proposant pas NSI | ~1 sur 3 | 2024 | Société informatique de France |
| Part de la voie générale en Terminale GT | 72,4 % | rentrée 2024 | DEPP |
| Campus connectés labellisés | 87 à 89 lieux | 2024-2025 | MESR / DGESIP |
| French Tech — Capitales et Communautés | 19 Capitales, 28 Communautés (France) | 2026-2028 | Mission French Tech |

### Éléments territoriaux (recherche documentaire, alimentent la colonne « Pourquoi »)

Campus NEXA : liste confirmée par NEXA — **Paris, Lyon, Lille**. Adresses relevées sur
[nexa.fr](https://www.nexa.fr/ecole), consultées le 15/08/2026.

Faits économiques territoriaux (Sophia Antipolis, COMCYBER et DGA-MI à Rennes, CEA-Leti et
STMicroelectronics à Grenoble, Michelin à Clermont-Ferrand, mutuelles niortaises, supercalculateur
Pangea à Pau, pôle Magelis à Angoulême, Naval Group à Brest et Lorient, UTBM à Belfort, UTT à Troyes,
gigafactories dunkerquoises) : sources publiques d'entreprise et institutionnelles, **non
individuellement horodatées** — ce sont des faits structurels stables, mobilisés comme éléments de
contexte et **non comme mesures**.

### Sources visées mais inaccessibles

`data.education.gouv.fr` · `data.gouv.fr` · `enseignementsup-recherche.gouv.fr` · ONISEP ·
Parcoursup · INSEE (API) · `geo.api.gouv.fr` — **toutes bloquées par la politique réseau de
l'environnement de production**. Voir `01-methodologie.md` §0.

---

## 4. Niveau de confiance par indicateur

| Indicateur | Confiance | Motif |
|---|---|---|
| Exclusion des 60 km, périmètres A et B | **élevée** | calcul déterministe sur référentiel officiel |
| Population, communes, départements, régions | **élevée** | INSEE / Etalab |
| Distances, étendue, concentration | **élevée** | calcul, sous réserve orthodromique vs routier |
| Composition des bassins | **élevée** | algorithme reproductible et documenté |
| `tle_estim` (vivier) | **moyenne** | proxy national, ignore la structure d'âge locale |
| Notes cyber / dev / data / marketing | **faible** | estimation experte, non issue de données scolaires |
| Note économie numérique | **moyenne** | ancrée sur des faits vérifiables, mais non quantifiée |
| Score global | **moyenne** | 20 % seulement entièrement observés |
| Classement P1 / P2 / P3 | **moyenne** | à réviser après enrichissement DEPP |
| Portefeuille de test recommandé | **moyenne-élevée** | repose surtout sur des critères observés (coût d'accès, concentration, opposition d'hypothèses) |

**En une phrase :** la géographie de ce livrable est solide, sa démographie est raisonnable, sa
dimension scolaire reste à établir.

---

## 5. Un point réglé depuis la première version

La liste des campus physiques NEXA a été **confirmée par NEXA : Paris, Lyon et Lille, et eux seuls**.
Une vérification de sensibilité avait été menée en incluant Bordeaux, Nantes et Marseille — des pages
campus existant à ces noms sur nexa.fr. Cette hypothèse est écartée.

Conséquence sur le livrable : six bassins majeurs (Marseille, Bordeaux, Nantes, Toulon,
Saint-Nazaire, Cholet) ont été **réintégrés à l'univers scoré**, qui passe de 53 à 59 bassins.
Marseille devient le premier bassin de France hors exclusion (~18 520 Terminales estimées) et le
classement P1 est modifié en conséquence. Toutes les distances d'accès sont désormais mesurées
depuis les trois bases réelles, ce qui a **fortement modifié le portefeuille de test recommandé** :
les zones du Grand Ouest, accessibles depuis un hypothétique campus nantais, sont devenues coûteuses.
