# 01 — Méthodologie réellement appliquée

Ce document décrit ce qui a été fait, dans l'ordre, et **les adaptations imposées par les données
réellement accessibles**. Les écarts par rapport à la méthode idéale sont signalés explicitement.

---

## 0. Contrainte de collecte — à lire d'abord

L'environnement de production disposait d'un accès réseau restreint. Concrètement :

| Source visée | Accessible ? | Conséquence |
|---|---|---|
| `data.education.gouv.fr` (API DEPP/Opendatasoft) | **Non** — bloqué | Pas d'effectifs par établissement, par série ni par spécialité |
| `data.gouv.fr`, `enseignementsup-recherche.gouv.fr`, ONISEP | **Non** — bloqué | Pas de liste Campus connectés, pas d'offre Parcoursup |
| INSEE / `geo.api.gouv.fr` | **Non** — bloqué | — |
| Référentiel Etalab `@etalab/decoupage-administratif` (npm) | **Oui** | Population légale INSEE, département, région, EPCI |
| Base officielle des codes postaux (La Poste, miroir GitHub) | **Oui** | Coordonnées GPS par code INSEE |
| Recherche web | **Oui** | Ancrages nationaux publiés, faits économiques territoriaux |

**Ce qui en découle, et qui structure tout le livrable :**

- l'ossature **géographique et démographique** de l'analyse est **observée et recalculable** ;
- l'ossature **scolaire** (Terminales, séries, spécialités) est un **proxy documenté** ;
- l'axe **affinité filières** est une **estimation experte**, pas une mesure.

Aucune valeur n'a été inventée pour combler un trou. Les colonnes non collectées sont marquées
`A_COLLECTER` et non remplies par zéro.

---

## 1. Exclusion géographique des zones de campus physiques

### Méthode

- Référentiel : **34 863 communes** géolocalisées (population légale INSEE via Etalab, coordonnées
  La Poste), couvrant **68,3 M habitants**.
- Distance **orthodromique** (formule de haversine, rayon terrestre 6 371,0088 km) entre le
  chef-lieu de chaque commune et chaque campus NEXA.
- Une commune est exclue si **min(distance aux campus) ≤ 60 km**.
- Le calcul est fait **commune par commune** : aucun département n'est exclu en bloc.

### Coordonnées des campus utilisées

| Campus | Adresse retenue | Coordonnées |
|---|---|---|
| Paris | 44bis quai de Jemmapes, 75010 | 48,8709 / 2,3646 |
| Lyon | centre-ville (secteur Bellecour) | 45,7578 / 4,8320 |
| Lille | 250 rue Madeleine Rebérioux, 59000 | 50,6216 / 3,0790 |
| *Bordeaux* (périmètre B) | 1 quai Armand Lalande, 33300 | 44,8672 / -0,5560 |
| *Nantes* (périmètre B) | 19 rue La Noue Bras de Fer, 44200 | 47,2043 / -1,5535 |
| *Marseille* (périmètre B) | Impasse Paradou, 13009 | 43,2555 / 5,3980 |

L'adresse exacte du campus de Lyon n'a pas été trouvée en source primaire ; le centre-ville a été
utilisé. **À 60 km de rayon, une imprécision de 2 km sur le centre est sans effet matériel** sur
la liste des communes exclues.

### Deux périmètres

- **Périmètre A** — la règle demandée (Paris, Lyon, Lille) : **2 982 communes, 19,1 M hab. (28,0 %)**.
- **Périmètre B** — sensibilité, les six campus réels : **4 040 communes, 25,4 M hab. (37,2 %)**.

### Résultat par département (extrait — fichier complet : `data/exclusion_departements.csv`)

| Dép. | % communes exclues (A) | % population exclue (A) | Statut |
|---|---|---|---|
| 92, 93, 94 | 100 % | 100 % | totalement exclus |
| 95 | 98,4 % | 99,9 % | majoritairement exclu |
| 69 Rhône | 97,7 % | 99,9 % | majoritairement exclu |
| 91 Essonne | 96,9 % | 99,2 % | majoritairement exclu |
| 78 Yvelines | 95,0 % | 99,0 % | majoritairement exclu |
| 59 Nord | 67,2 % | 82,2 % | majoritairement exclu |
| 77 Seine-et-Marne | 56,4 % | 83,1 % | majoritairement exclu |
| 42 Loire | 52,8 % | 72,7 % | majoritairement exclu |
| **62 Pas-de-Calais** | 45,8 % | 62,6 % | **partiellement — reste exploitable** |
| **01 Ain** | 46,5 % | 52,0 % | **partiellement — reste exploitable** |
| **38 Isère** | 40,6 % | 37,6 % | **partiellement — reste exploitable** |
| **60 Oise** | 36,2 % | 54,3 % | **partiellement — reste exploitable** |
| **07 Ardèche, 26 Drôme, 71 Saône-et-Loire, 28 Eure-et-Loir** | < 8 % | < 15 % | **marginalement touchés** |

Deux conséquences commercialement importantes :

- **Saint-Étienne est exclu** (≈ 51 km de Lyon), ainsi que **Valenciennes, Arras, Douai, Béthune**
  (< 60 km de Lille) et **Beauvais, Compiègne, Chartres nord, Creil** (< 60 km de Paris). Ces
  bassins, souvent cités spontanément comme « villes moyennes intéressantes », **sortent du champ**
  du campus À distance.
- **L'Isère reste exploitable à 59 %** : Grenoble est à 94 km de Lyon et demeure pleinement dans le
  périmètre. De même, une large moitié du Pas-de-Calais (Boulogne, Calais, Montreuil) reste ouverte.

---

## 2. Construction des bassins d'opportunité — pas de découpage administratif

L'unité commerciale recherchée est le **bassin d'activation IE**, pas le département. La construction
est **algorithmique et data-driven**, pas déclarative :

1. **Villes-centres candidates** : communes de ≥ 15 000 hab., hors exclusion A, qui sont un
   **maximum local de population dans un rayon de 12 km**. Ce filtre évite qu'un bassin soit centré
   sur une banlieue (sans lui, l'algorithme centrait le bassin bordelais sur Le Bouscat et le bassin
   nantais sur Bouguenais). 377 candidates → **231 maxima locaux**.
2. **Rayon de bassin : 30 km** autour de la ville-centre — soit ~45 min de trajet, l'amplitude
   réaliste d'une tournée IE dans la journée.
3. **Sélection gloutonne** : on retient à chaque tour la ville-centre dont le bassin capte la plus
   grande population **encore non attribuée**, puis on retire ces communes du pool. Les bassins sont
   donc **disjoints** — pas de double comptage du vivier.
4. **Seuil d'arrêt** : 110 000 habitants captés (en dessous, une zone ne justifie pas une tournée).
5. Chaque bassin est **nommé d'après sa commune la plus peuplée**, et toutes ses distances sont
   mesurées depuis cette ville principale.

**75 bassins** sont produits. Ils traversent librement les frontières administratives quand la
géographie le justifie : *Montpellier–Nîmes* (34+30), *Dunkerque–Calais* (59+62), *Metz–Thionville*
(57+54), *Belfort–Montbéliard* (25+90+70), *Annecy–Annemasse–Genevois* (74+01), *Béziers–Narbonne*
(34+11).

### Univers retenu : 53 bassins

- Les **8 bassins situés à ≤ 60 km d'un campus NEXA réel** (périmètre B) sont écartés du scoring :
  Marseille, Bordeaux, Nantes, Toulon, Saint-Nazaire, Cholet, La Roche-sur-Yon, La Teste-de-Buch.
- Les bassins de plus de 250 000 habitants sont retenus (**49**).
- **4 villes moyennes sous le seuil** sont ajoutées délibérément pour rendre **H7 testable** :
  Troyes, Angoulême, Niort, Albi. Sans elles, l'hypothèse « les villes moyennes sont un marché
  intéressant » serait invérifiable, l'échantillon ne contenant que des agglomérations.

Le total de 53 dépasse légèrement la fourchette indicative de 30–50 ; conformément à la consigne,
aucune zone pertinente n'a été supprimée pour atteindre un chiffre rond.

---

## 3. Les quatre axes du score

### Axe 1 — Vivier B1 (40 %) · **PROXY**

Faute d'effectifs DEPP, le vivier est estimé par :

```
Terminales estimées = population du bassin × 1,05 %
```

Le ratio provient d'ancrages nationaux publiés (rentrée 2024) : ~1,597 M élèves en formations
générales et technologiques et ~651 000 en voie professionnelle en lycée, soit de l'ordre de
**720 000 élèves de Terminale** pour ~68,3 M habitants.

**Ce que ce proxy ignore** : la structure par âge locale, les taux de scolarisation, l'attractivité
scolaire d'une ville sur sa périphérie, le poids du privé. Il est donc **fiable en ordre de grandeur
et pour comparer des bassins, pas pour dimensionner une campagne**.

Normalisation en **racine carrée** avant mise à l'échelle 0–100 : cela atténue le biais métropolitain
sans l'effacer (une agglomération 4 fois plus peuplée n'obtient que 2 fois plus de points).

### Axe 2 — Affinité avec les filières NEXA (25 %) · **ESTIMATION EXPERTE**

**Cet axe n'est pas mesuré.** Il devait reposer sur les effectifs NSI, STI2D, Bac Pro CIEL, STMG et
mathématiques par établissement — données inaccessibles ici.

À la place, chaque bassin reçoit **quatre notes de 1 à 5** (cyber, développement, data/IA, marketing)
fondées sur son **tissu économique et industriel documenté**, avec une justification factuelle
consignée dans la colonne « Pourquoi ». Exemples de raisonnement :

- base industrielle/mécatronique/électronique → vivier probable STI2D et Bac Pro CIEL → cyber & dev ;
- présence d'assurance, mutualité, banque, calcul intensif → data/IA ;
- économie tertiaire, tourisme, commerce, marque → STMG et générales → marketing digital.

`potentiel_nexa_global` = moyenne des quatre notes, ramenée sur 100.

**Limite à retenir** : la présence d'une industrie dans un bassin n'établit pas que ses lycées
proposent NSI ou CIEL. Un tiers des lycées français ne propose toujours pas NSI, et NSI ne représente
que **4,0 % des élèves de Terminale générale en 2025** (4,5 % en 2024) — un vivier national étroit
et très inégalement réparti. **Cet axe doit être remplacé par les données DEPP avant toute décision
d'allocation budgétaire.**

### Axe 3 — Concentration géographique (20 %) · **OBSERVÉ**

Entièrement calculé, sans proxy :

```
concentration = 0,40 × part de la population à ≤ 20 km du centre
              + 0,35 × pénalité d'étendue (100 à ≤ 25 km ; 0 à ≥ 60 km entre villes de ≥ 10 000 hab.)
              + 0,25 × nombre de villes de ≥ 10 000 hab. (plafonné à 10)
```

La troisième composante mesure la **capacité à enchaîner plusieurs IE** sur une même tournée : un
bassin d'une seule grande ville est concentré mais offre peu de points d'appui.

### Axe 4 — Potentiel économique numérique (15 %) · **ESTIMATION EXPERTE**

Note de 1 à 5, ancrée sur des faits vérifiables : labels French Tech (19 Capitales et 28 Communautés
pour 2026-2028), grands employeurs à besoins numériques, technopôles, projets d'implantation.

Conformément à la consigne, l'analyse **ne se limite pas aux start-up** : Niort est noté 4 pour ses
mutuelles, Pau 4 pour le supercalculateur de TotalEnergies, Le Havre 3 pour la cybersécurité portuaire.
Un potentiel économique faible **n'élimine jamais une zone** — il ne pèse que 15 %.

### Score final

```
score = 0,40 × vivier + 0,25 × affinité + 0,20 × concentration + 0,15 × économie numérique
```

Les pondérations du brief ont été conservées. **Ce n'est pas neutre** : l'axe le plus lourd (40 %)
est aussi celui reposant sur un proxy, et le deuxième (25 %) sur un jugement expert. Le score doit
donc être lu comme un **outil de tri et de discussion**, pas comme une mesure.

---

## 4. Ce qui a été délibérément exclu du score

Aucune de ces variables n'entre dans le calcul, conformément à la consigne :

éloignement d'une université · absence d'école numérique · ruralité · présence d'un Campus connecté ·
coût du logement étudiant · densité d'enseignement supérieur · IPS · profil socio-économique.

Elles sont **collectées séparément** (voir `04-hypotheses-experimentales.md`) comme variables
expérimentales, destinées à être confrontées aux résultats commerciaux réels de l'année 1.

**Effet observable de cette règle, et il est frappant** : les 12 zones P1 contiennent **toutes** un
pôle étudiant majeur. Le score, ne récompensant que le volume, l'affinité, la concentration et
l'économie, désigne mécaniquement des territoires bien dotés en enseignement supérieur — c'est-à-dire
exactement l'inverse de l'hypothèse intuitive du « territoire idéal pour le distanciel ».
Cette tension est **le principal enseignement méthodologique de l'étape 1**, et elle justifie à elle
seule que le portefeuille de test ne soit pas constitué des seuls P1.

---

## 5. Traçabilité

Chaque indicateur du fichier `data/bassins_scores.csv` relève d'une des cinq natures suivantes :

| Nature | Colonnes concernées |
|---|---|
| **Donnée observée** | population, communes, départements, régions, distances, étendue, concentration, exclusion |
| **Proxy** | `tle_estim` (population × 1,05 %) |
| **Estimation experte** | `cyber`, `dev`, `data`, `mkt`, `eco` |
| **Hypothèse** | pondérations du score, table d'affinité série → filière |
| **Interprétation** | colonne `why`, priorités P1/P2/P3, portefeuille recommandé |

Les scripts de `pipeline/` régénèrent l'intégralité des résultats à partir des seuls référentiels
publics : toute valeur du livrable est recalculable.
