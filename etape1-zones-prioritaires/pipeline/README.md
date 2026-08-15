# Pipeline reproductible

Tous les résultats du livrable sont régénérables à partir de référentiels publics uniquement.
Aucune dépendance autre que Python 3 et `numpy`.

```bash
pip install numpy
python3 01_telechargement_referentiels.py   # réseau requis (npm + GitHub)
python3 02_bassins.py                        # exclusion 60 km + construction des 75 bassins
python3 03_scoring.py                        # score d'opportunité territoriale, 53 bassins retenus
python3 04_exclusion_export.py               # périmètre d'exclusion par département
python3 06_livrables.py                      # tableau de synthèse + handoff étape 2
```

Vérifié : la chaîne `02 → 06` régénère `data/bassins_scores.json` **à l'identique** (même empreinte MD5).

## Le script à lancer en priorité

```bash
python3 05_enrichissement_depp.py --inspect   # liste les champs réels des datasets DEPP
python3 05_enrichissement_depp.py --run       # télécharge et rattache aux bassins
```

Ce script **n'a pas pu être exécuté** lors de la production de l'étude : l'environnement bloquait
`data.education.gouv.fr` (il échoue explicitement avec `Tunnel connection failed: 403`). Il remplace
les deux approximations majeures du livrable :

| Colonne | Statut actuel | Après exécution |
|---|---|---|
| `tle_estim` | PROXY (population × 1,05 %) | effectifs Terminale réels par établissement |
| `cyber`, `dev`, `data`, `mkt` | ESTIMATION EXPERTE (tissu économique) | effectifs NSI / STI2D / CIEL / STMG agrégés |
| `nb_lycees` | non collecté | comptage réel par bassin |
| `ips_moyen` | non collecté | IPS moyen des lycées du bassin |

Après exécution, rejouer `03_scoring.py` : **le classement P1/P2/P3 doit être considéré comme
provisoire tant que cette étape n'a pas été faite.**

## Paramètres modifiables

| Fichier | Paramètre | Valeur | Effet |
|---|---|---|---|
| `02_bassins.py` | `RAYON` | 30 km | amplitude d'une tournée IE ; à 35 km les bassins fusionnent (Montpellier absorbe Nîmes plus largement) |
| `02_bassins.py` | `RAYON_EXCL` | 60 km | règle d'exclusion des campus |
| `02_bassins.py` | `CAMPUS_A` / `CAMPUS_B` | 3 / 6 campus | périmètre A = règle du brief ; B = campus NEXA réels |
| `02_bassins.py` | `POP_MIN_POLE` | 15 000 hab. | seuil de crédibilité d'une ville-centre |
| `02_bassins.py` | `RATIO_TLE` | 0,0105 | proxy Terminale/population — **à supprimer après enrichissement DEPP** |
| `03_scoring.py` | pondérations | 40/25/20/15 | cadre du brief |
| `03_scoring.py` | `EXP` | notes 1–5 | table des estimations expertes, avec justification par bassin |

## Sources des référentiels

- **`@etalab/decoupage-administratif`** (npm, v6.0.0) — Etalab/INSEE : population légale, département,
  région, EPCI.
- **`high54/Communes-France-JSON`** (GitHub) — miroir de la base officielle des codes postaux
  (La Poste) : coordonnées GPS par code INSEE.

`gpsfix.py` complète la géolocalisation de Paris, Lyon et Marseille, codés par arrondissement dans le
référentiel La Poste (sans ce correctif, 4,1 M habitants manquaient à l'analyse).
