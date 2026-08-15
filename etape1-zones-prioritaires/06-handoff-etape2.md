# 06 — Ce que l'étape 2 reçoit

L'étape 2 consiste à **rechercher exhaustivement les établissements de chaque périmètre retenu et à
les classer P1/P2/P3**. Elle ne doit pas rejouer l'analyse territoriale.

**Fichier d'entrée : [`data/handoff_etape2.json`](data/handoff_etape2.json)** — 53 zones, une entrée
par bassin.

---

## Structure d'une entrée

```json
{
  "bassin": "Vannes",
  "priorite": "P2",
  "rang": 19,
  "perimetre": {
    "pole_centre": { "commune": "Vannes", "lat": 47.6598, "lon": -2.757 },
    "rayon_km": 30,
    "departements": ["56 Morbihan"],
    "regions": ["Bretagne"],
    "villes_principales": ["Vannes (56k)", "Auray (14k)", "Saint-Avé (12k)",
                           "Séné (10k)", "Sarzeau (9k)"],
    "nb_communes": 86
  },
  "potentiel_estime": {
    "population_bassin": 329766,
    "terminale_estimee": 3460,
    "nature": "PROXY population x 1,05 % - a remplacer par effectifs DEPP"
  },
  "filieres_nexa_prioritaires": ["Cyber"],
  "potentiels_par_filiere_1a5": {
    "cyber": 5, "developpement": 4, "data_ia": 3, "marketing": 4,
    "nature": "ESTIMATION EXPERTE"
  },
  "raisons_de_selection": "Pôle cyber breton (Vannes-Ploërmel), DGA, Université Bretagne Sud, ESN",
  "variables_experimentales": {
    "distance_pole_etudiant_majeur_km": 46.9,
    "contient_pole_etudiant_majeur": false,
    "distance_campus_nexa_km": 103.7,
    "campus_nexa_le_plus_proche": "Nantes",
    "concentration_20km_pct": 68.0,
    "etendue_villes_km": 16.5,
    "campus_connecte": "A_COLLECTER (source DGESIP)",
    "offre_superieure_numerique_locale": "A_COLLECTER (Parcoursup / ONISEP)",
    "ips_moyen_lycees": "A_COLLECTER (fr-en-ips-lycees)"
  },
  "hypotheses_a_tester": [
    "H1 - faible offre supérieure locale : la zone convertit-elle mieux ?",
    "H2 - éloignement du pôle étudiant majeur (47 km)",
    "H3 - économie numérique dynamique : effet sur l'intérêt pour NEXA",
    "H5 - concentration NSI/STI2D/CIEL supposée : surperformance Cyber/Dev à vérifier",
    "H6 - vivier STMG/généraliste supposé : performance Marketing Digital à vérifier",
    "H7 - ville moyenne : rendement par IE supérieur aux métropoles ?",
    "H8 - présence d'un Campus connecté : A COLLECTER (DGESIP) avant lancement"
  ]
}
```

Le **périmètre est défini géométriquement** — un point central et un rayon de 30 km — et non par une
liste de communes. C'est volontaire : l'étape 2 doit requêter l'Annuaire de l'éducation par
géolocalisation, ce qui garantit l'exhaustivité et évite les oublis de communes périphériques.

---

## Requête type pour l'étape 2

```python
# Tous les lycées d'un bassin, via l'Annuaire de l'éducation
# https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records
params = {
    "where": f'distance(position, geom\'POINT({lon} {lat})\', {rayon_km}km) '
             f'and type_etablissement="Lycée"',
    "limit": 100,
}
```

Puis, pour chaque établissement trouvé, joindre les effectifs Terminale et les spécialités depuis
`fr-en-lycee_gt-effectifs-niveau-sexe-lv`, `fr-en-lycee_pro-effectifs-niveau-sexe-lv` et
`fr-en-effectifs-specialites-doublettes-terminale-generale`, via le **numéro UAI**.

---

## Ce que l'étape 2 doit produire, et pas ce que l'étape 1 a produit

L'étape 1 répond à *où tester*. L'étape 2 répond à *quels établissements contacter*, et devra classer
chaque lycée sur des critères que l'étape territoriale ne peut pas trancher :

| Critère de classement lycée | Donnée nécessaire |
|---|---|
| Volume de Terminales de l'établissement | effectifs DEPP par UAI |
| Présence des spécialités et séries cibles (NSI, STI2D, CIEL, STMG) | effectifs par spécialité / série |
| Nombre de familles NEXA adressables dans le même établissement | dérivé |
| Existence d'un BTS/BUT numérique sur place (concurrence directe) | annuaire + Parcoursup |
| Accessibilité depuis le point de tournée | temps de trajet routier |
| Historique de relation NEXA | CRM interne |

---

## Ordre de priorité recommandé pour l'étape 2

Ne pas lancer la recherche établissement sur les 53 bassins. Suivre l'ordre suivant :

1. **Les 8 bassins du portefeuille de test** (voir [README](README.md)) — Rennes, Grenoble, Rouen,
   Angers, Toulouse, Niort, Vannes, Béziers. Ce sont les seuls à activer en année 1.
2. **Les 4 autres P1** — Nice, Montpellier–Nîmes, Strasbourg, Clermont-Ferrand, Tours, Annecy,
   La Réunion — en réserve, activables si la saison avance plus vite que prévu.
3. **Les P2 et P3** — uniquement après les résultats de mi-saison, en fonction de ce que les
   premières zones auront appris.

---

## Trois arbitrages à trancher avant de lancer l'étape 2

1. **Le périmètre d'exclusion.** NEXA opère six campus. Faut-il neutraliser les six (périmètre B,
   retenu ici) ou seulement Paris/Lyon/Lille (périmètre A, la règle littérale) ? Si A, alors
   Marseille (~18 520 Terminales estimées) et Bordeaux (~12 650) réintègrent l'univers en tête de
   classement, ce qui change entièrement le portefeuille.

2. **L'enrichissement DEPP.** Lancer `pipeline/05_enrichissement_depp.py` depuis un poste au réseau
   ouvert, puis rejouer `03_scoring.py`. Le classement P1/P2/P3 **doit être considéré comme
   provisoire** tant que l'axe affinité (25 % du score) repose sur du jugement expert.

3. **L'instrumentation du CRM.** Créer le champ « bassin d'opportunité » sur l'objet lycée et
   l'alimenter depuis `handoff_etape2.json` **avant la première IE**. Sans lui, aucune des huit
   hypothèses ne sera vérifiable en fin de saison, et l'année 2 repartira des mêmes intuitions que
   l'année 1.
