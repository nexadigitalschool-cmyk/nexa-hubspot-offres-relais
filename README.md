# NEXA — Socle national des lycées (étape 1)

Pipeline reproductible qui construit le **socle national des lycées** à partir de
l'**Annuaire de l'éducation nationale** (dataset officiel
[`fr-en-annuaire-education`](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/)),
première étape de la base de prospection des campus NEXA Digital School.

Cette passe s'arrête au socle : **pas** d'enrichissement ONISEP, effectifs, IPS ou
Parcoursup, et **aucun import HubSpot**.

---

## 1. Ce que fait le pipeline

1. Charge la configuration des campus / académies / départements / filtres
   (`config/campuses.yml`).
2. Interroge l'API **Opendatasoft Explore v2.1** de la source, avec **pagination
   complète** par `offset` jusqu'à épuisement, et :
   - timeout par requête, **retry** avec **backoff** exponentiel (respect de
     `Retry-After`), **limitation du rythme** des appels,
   - **sauvegarde des réponses brutes** (une par page), **reprise sur erreur**
     (les pages déjà écrites sont relues, pas refetchées).
3. **Vérifie le schéma réel** du dataset (les noms de champ sont résolus auprès
   de la source, jamais devinés) et **journalise tout écart** (renommage/format).
4. **Filtre** les lycées : général et technologique, professionnel, polyvalent —
   et **exclut** collèges, écoles, établissements étrangers / AEFE, fermés.
5. **Normalise sans altérer** : UAI, SIREN, SIRET, code postal conservés en
   **texte** (zéros initiaux préservés) ; téléphone normalisé dans un **champ
   séparé** ; e-mail institutionnel `ce.` conservé tel quel.
6. Utilise l'**UAI** comme identifiant principal et **détecte / journalise** :
   UAI absent, UAI invalide, doublons UAI, établissement sans commune,
   coordonnées GPS absentes, champs renommés.
7. **Affecte un campus** (par académie, priorité au département prioritaire).
8. Calcule la **distance à vol d'oiseau (km)** *uniquement si* les coordonnées du
   campus sont fournies (sinon calcul désactivé proprement). Cette distance
   **n'est jamais** un temps de transport.
9. Ne produit **aucune donnée nominative** (pas de nom de proviseur, pas d'e-mail
   personnel reconstruit).

Aucun résultat n'est supprimé silencieusement : toute ligne écartée est versée
dans `rejected.csv` avec un **motif précis**.

---

## 2. Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .          # installe requests + PyYAML
# ou, sans installation :  export PYTHONPATH=src
```

Python ≥ 3.10.

---

## 3. Lancer le pipeline

### Périmètre pilote (Paris / Créteil / Versailles), source officielle

```bash
python -m ie_prospection.pipeline --config config/campuses.yml --source api
```

> ⚠️ Nécessite un **accès réseau sortant** vers `data.education.gouv.fr`
> (ou un miroir Opendatasoft). Voir §6.

### Démonstration hors-ligne (données synthétiques)

Quand l'accès réseau n'est pas ouvert, on exécute la **même chaîne** sur un jeu
synthétique reproduisant la forme de l'API (noms de champs réels, cas limites) :

```bash
python -m ie_prospection.pipeline --config config/campuses.yml --source fixture
```

### Options utiles

| Option | Rôle |
| --- | --- |
| `--base-url URL` | forcer un miroir Opendatasoft (voir `config/campuses.yml`) |
| `--no-resume` | ignorer les pages brutes déjà sauvegardées |
| `--limit-per-academie N` | plafonner le volume par académie (tests/diagnostic) |
| `--run-id ID` | identifiant de run (nom du journal) |

---

## 4. Sorties produites

| Fichier | Contenu |
| --- | --- |
| `data/raw/<académie>/page_*.json` | réponses brutes de l'API (une par page) |
| `data/intermediate/annuaire_records.jsonl` | enregistrements bruts agrégés |
| `data/output/socle_national.csv` | **socle national nettoyé** (schéma ci-dessous) |
| `data/output/campus_<nom>.csv` | un fichier par campus configuré actif |
| `data/output/rejected.csv` | lignes rejetées **avec motif** |
| `reports/run_<id>.log` | journal d'exécution |
| `reports/data_quality_report.md` / `.json` | rapport de qualité |
| `reports/sources.csv` / `.json` | sources, URLs, dates d'extraction, volumes |
| `reports/echantillon_30.csv` | échantillon de 30 lignes pour relecture humaine |

### Schéma du socle (`socle_national.csv`)

`UAI`, `Nom`, `Type`, `Statut public/privé`, `Adresse`, `CP`, `Commune`,
`Académie`, `Département`, `Région`, `Téléphone`, `Mail ce.`, `Site web`,
`SIREN`, `SIRET`, `Latitude`, `Longitude`, `Campus rattaché`,
`Distance campus km`, `Source`, `Date extraction`.

---

## 5. Configuration (`config/campuses.yml`)

- `campuses[].active: true` définit le **périmètre extrait** (le pilote Paris est
  actif ; Lyon, Lille, Bordeaux, Nantes, À distance sont préconfigurés et
  inactifs).
- `campuses[].academies` : académies interrogées.
- `campuses[].priority_departments` : départements prioritaires pour
  l'affectation (ex. `033` pour Bordeaux, `044` pour Nantes).
- `campuses[].latitude / longitude` : **`null` par défaut — à compléter par NEXA**.
  Tant qu'elles sont absentes, le calcul de distance est **désactivé** pour ce
  campus (`Distance campus km` reste vide et est comptabilisé comme manquant).
  **Ne jamais inventer ces coordonnées.**
- `lycee_filter` : familles de lycées retenues, exclusions, ouverts uniquement.

---

## 6. Vérification de la source (à faire au 1er run live)

Conformément au principe « ne pas se fier à la mémoire », le pipeline **vérifie
le schéma** au démarrage (`GET /catalog/datasets/{id}`) et résout les vrais noms
de champ. Au premier run réel, contrôler dans le journal :

- le `total_count` par académie (fenêtre de pagination v2.1 = `offset+limit ≤ 10000` ;
  si une académie dépasse, restreindre par département) ;
- l'absence d'avertissement « champ jamais résolu » (sinon un champ a été
  renommé : mettre à jour `FIELD_MAP` dans `src/ie_prospection/schema.py`) ;
- la « distribution nature/type rencontrée » du rapport qualité, pour confirmer
  que la liste blanche `lycee_filter.keep_natures` couvre bien les libellés réels.

---

## 7. Tests

```bash
pip install pytest
pytest -q
```

Les tests couvrent notamment : **pagination au-delà de 100 lignes**, **doublons
UAI**, **zéros initiaux**, **erreurs API** (400 / 429 / 5xx + retry), **champs
manquants / renommés**, affectation campus et distance.

---

## 8. Structure

```
config/campuses.yml            # configuration campus / filtres
src/ie_prospection/
  config.py                    # chargement + validation de la config
  schema.py                    # schéma de sortie + cartographie des champs
  ods_client.py                # client API (pagination, retry, backoff, reprise)
  transform.py                 # filtrage, normalisation, dédup, campus, distance
  geo.py                       # distance orthodromique (à vol d'oiseau)
  reporting.py                 # écriture CSV / rapport qualité / manifeste
  fixtures.py                  # jeu synthétique hors-ligne
  pipeline.py                  # orchestration + CLI
tests/                         # suite pytest
data/{raw,intermediate,output} # données (non versionnées)
reports/                       # journaux + rapports
```
