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
7. **Affecte un campus** (au plus proche par distance quand les coordonnées sont
   connues, sinon par académie / département prioritaire).
8. **Géocode l'adresse du campus** via la **Base Adresse Nationale** officielle
   (`api-adresse.data.gouv.fr`) — jamais de coordonnées inventées — puis calcule
   la **distance à vol d'oiseau (km)** (sinon calcul désactivé proprement). Cette
   distance **n'est jamais** un temps de transport.
9. **Règle de rayon (60 km)** : les académies principales (Paris/Créteil/
   Versailles, dont **la Seine-et-Marne 77 en intégralité**) sont conservées
   sans condition ; les **départements « tampons » d'autres académies**
   (Eure 27, Eure-et-Loir 28, Loiret 45, Oise 60) ne sont conservés que si
   l'établissement est **réellement à moins de 60 km** du campus. Les cas non
   vérifiables (GPS manquant) sont rejetés avec motif, jamais devinés.
9. Ne produit **aucune donnée nominative** (pas de nom de proviseur, pas d'e-mail
   personnel reconstruit).

Aucun résultat n'est supprimé silencieusement : toute ligne écartée est versée
dans `rejected.csv` avec un **motif précis** (`type_hors_perimetre`,
`etablissement_ferme`, `hors_perimetre_etranger`, `uai_absent`, `uai_invalide`,
`doublon_uai`, `hors_rayon_km`, `distance_non_verifiable`, …).

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
| `--geocode` | (re)géocoder les adresses de campus via la BAN officielle |
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
- `campuses[].priority_departments` : départements prioritaires (Paris couvre
  toute l'Île-de-France : `075,077,078,091,092,093,094,095`).
- `campuses[].buffer_departments` : départements **d'autres académies** à
  surveiller (Paris : `027,028,045,060`) — conservés seulement si < `radius_km`.
- `campuses[].radius_km` : rayon de conservation des tampons (défaut **60**).
- `campuses[].address` : adresse du campus, **géocodée via la BAN** au run
  (renseigne lat/lon, provenance dans `coordinates_source`). Le campus Paris
  (`44 bis quai de Jemmapes, 75010`) est pré-renseigné et re-dérivable via
  `--geocode`. Sans adresse ni coordonnées, la distance est **désactivée**.
  **Les coordonnées ne sont jamais inventées.**
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
manquants / renommés**, **règle des 60 km** (tampon conservé / hors rayon /
distance non vérifiable), **géocodage BAN**, affectation campus et distance.
30 tests, tous verts.

---

## 8. Étape 2 — Enrichissement public (Paris, < 60 km)

Enrichit le socle Paris **restreint aux établissements à moins de 60 km** du
campus, à partir de sources **publiques externes uniquement** — aucune donnée
HubSpot / My Future / interne, **aucun contact nominatif**, **aucun scoring**.

```bash
# Démonstration hors-ligne (données d'enrichissement synthétiques) :
python -m ie_prospection.enrich.pipeline2 --source fixture
# Sources publiques réelles (dès l'egress ouvert) :
python -m ie_prospection.enrich.pipeline2 --source api
```

**Sources** (jointure **exclusivement sur l'UAI**, jamais sur le nom) :
ONISEP Idéo-Structures, ONISEP Idéo-Formations, effectifs officiels des lycées,
IPS, Parcoursup, état ouvert/fermé (annuaire), et sites officiels des
établissements (détection *bureau des entreprises* / *forum d'orientation* par
mots-clés). Chaque source qui échoue est **poursuivie avec des valeurs vides et
documentée** (rapport de jointures).

**Variables ajoutées** : filières `NSI/SNT/STI2D/STMG/bac pro SN`, `Effectif
élèves`, `IPS`, `BTS ou post-bac`, `État établissement`, `Bureau des
entreprises`, `Forum ou événement orientation`, plus **Source + Date par
donnée**.

**Livrables** :

| Fichier | Contenu |
| --- | --- |
| `data/output/paris/02_enrichissement_public_paris.csv` / `.xlsx` | socle enrichi |
| `reports/paris/02_jointures.md` | taux de jointure et de complétude par source |
| `reports/paris/02_anomalies.csv` | anomalies (join miss, fermé, hors 60 km, …) |
| `reports/paris/02_controle_30_lignes.xlsx` | échantillon 30 lignes (relecture) |

> Comme à l'étape 1, les identifiants de datasets et noms de champs sont
> **validés au premier run en ligne** (aucun endpoint inventé). Toutes les
> sources d'enrichissement sont hébergées sur des domaines actuellement bloqués
> par l'egress de cet environnement : le mode `fixture` démontre la chaîne
> complète, le mode `api` se dégrade proprement et documente l'indisponibilité.
>
> **Données réelles** : `data/output/paris/01_socle_paris.csv` (601 lycées) et
> `data/output/socle_national.csv` (620) sont les **socles réels** issus de
> l'Annuaire (open data publique), versionnés comme référence. Le lecteur gère
> le séparateur `;`, le BOM et **préserve toutes les colonnes** du socle (dont
> `Téléphone normalisé`, `Règle d'inclusion`, …). Sur ces données, `--source api`
> conserve les **592 lycées à < 60 km** (9 exclus > 60 km) ; dans cet
> environnement **tous les domaines externes sont bloqués par l'egress**
> (open data ET sites d'établissement renvoient 403 via le proxy), donc les
> **7 sources sont indisponibles (0 % de jointure)** et l'enrichissement reste
> vide — documenté dans `02_jointures.md`. Deux garde-fous de fiabilité ont été
> ajoutés à cette occasion : un HTTP ≥ 400 (403 du proxy) n'est jamais compté
> comme site exploitable, et un `robots.txt` 404 vaut « autorisé ».

## 9. Étape 4 — Enrichissement nominatif (Paris, tous les lycées)

Recherche de **contacts professionnels publics** pour **tous** les lycées du
fichier Paris (aucun filtre P1/P2/P3), dans l'ordre imposé : site officiel de
l'établissement → site de l'académie → annuaire institutionnel → page
professionnelle publique → LinkedIn/Sales Navigator **uniquement si un accès
légal est déjà configuré** (désactivé par défaut).

```bash
python -m ie_prospection.enrich_nominatif.pipeline4
# entrée : 03_base_finale_paris.xlsx si présent, sinon 02_enrichissement_public_paris.xlsx
```

**Garde-fous appliqués par le code** (règles impératives) : aucun nom inventé
(on n'extrait que du texte réellement présent, avec **extrait de preuve** et
URL), aucun email déduit sans preuve, aucun téléphone créé — les coordonnées
sont bornées à l'entrée du contact pour ne jamais capter celles du voisin ;
les emails **académiques reconstruits** (à partir d'un nom réel) sont marqués
**Non vérifié** ; les emails **génériques** du lycée restent dans l'onglet
Établissements ; **robots.txt respecté** (abstention si inaccessible) ; source +
date conservées ; **max 5 contacts** par établissement ; si aucun contact :
le lycée est conservé et marqué **« Contact nominatif non trouvé »**. Aucun
envoi, aucun import HubSpot.

**Profils** : Décideur (proviseur, adjoint), Facilitateur (DDFPT, bureau des
entreprises), Prescripteur (référent orientation, prof documentaliste/CDI).

**Livrables** :

| Fichier | Contenu |
| --- | --- |
| `data/output/paris/04_enrichissement_nominatif_paris.xlsx` | onglets **Établissements** + **Contacts** |
| `reports/paris/04_lycees_sans_contact.csv` | lycées sans contact + raisons |
| `reports/paris/04_emails_a_verifier.csv` | emails à valider (dont reconstruits) |
| `reports/paris/04_sources_utilisees.csv` | statut de chaque source de la cascade |

> Toutes les sources web sont bloquées par l'egress de cet environnement (les
> sites d'établissement renvoient 403 via le proxy, `robots.txt` inclus) : le
> harnais s'exécute réellement sur les **592 lycées réels**, respecte les
> robots.txt et se solde par « Contact nominatif non trouvé » pour tous
> (aucune donnée inventée). La logique d'extraction est validée par des tests
> unitaires sur pages HTML factices. Dès qu'un accès sortant vers les sites
> d'établissement sera ouvert, le même `--source api` extraira les contacts
> réellement publiés.

## 10. Structure

```
config/campuses.yml            # configuration campus / filtres
src/ie_prospection/
  config.py                    # chargement + validation de la config
  schema.py                    # schéma de sortie + cartographie des champs
  ods_client.py                # client API (pagination, retry, backoff, reprise)
  transform.py                 # filtrage, normalisation, dédup, campus, rayon 60 km
  geo.py                       # distance orthodromique (à vol d'oiseau)
  geocode.py                   # géocodage des campus via la BAN officielle
  reporting.py                 # écriture CSV / rapport qualité / manifeste
  fixtures.py                  # jeu synthétique hors-ligne
  pipeline.py                  # orchestration + CLI (étape 1)
  enrich/                      # ÉTAPE 2 — enrichissement public (Paris < 60 km)
    schema2.py                 #   colonnes d'enrichissement + spéc. des sources
    fetchers.py                #   récupération ODS/ONISEP/sites (best-effort)
    build.py                   #   jointures UAI, complétude, anomalies
    fixtures2.py               #   enrichissement synthétique hors-ligne
    xlsx.py                    #   écriture .xlsx
    pipeline2.py               #   orchestration + CLI (étape 2)
  enrich_nominatif/            # ÉTAPE 4 — contacts professionnels publics
    schema4.py                 #   colonnes, rôles ciblés, profils, emails
    robots.py                  #   respect des robots.txt
    extractors.py              #   extraction sans invention (+ preuve)
    sources4.py                #   cascade de sources publiques
    build4.py                  #   onglets + rapports
    pipeline4.py               #   orchestration + CLI (étape 4)
tests/                         # suite pytest
data/{raw,intermediate,output} # données (non versionnées)
reports/                       # journaux + rapports
```
