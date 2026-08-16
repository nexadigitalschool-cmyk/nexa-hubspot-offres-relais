# Chaîne faceless — méthode et outillage

Une chaîne « faceless » est un compte où on ne montre jamais son visage : le contenu
est écrit, illustré et monté à l'IA.

Ce document couvre l'outillage installé dans le dépôt. La méthode elle-même est dans
la skill `/faceless` (`.claude/skills/faceless/SKILL.md`), qui l'exécute étape par
étape.

---

## Le pipeline

```
niche  →  collecte  →  pattern  →  script  →  visuels  →  montage
 ↓          ↓            ↓          ↓          ↓           ↓
test 50   yt-trans-   agent      agent     Higgsfield  agent
vidéos    cripts.py   analyse    redaction    MCP       montage
```

Chaque étape est autonome : on peut entrer par n'importe laquelle.

---

## 1. Choisir la niche

Le seul test qui compte : **tiendriez-vous 50 vidéos sur ce sujet sans vous lasser ?**
Une chaîne faceless ne rentabilise pas avant plusieurs dizaines d'épisodes.

Niches qui fonctionnent en format court : vulgarisation scientifique, histoire
méconnue, psychologie et biais cognitifs, finance personnelle, true crime, mythologie,
santé, anecdotes business.

---

## 2. Collecter les transcriptions — `scripts/yt-transcripts.py`

C'est le script que la méthode d'origine vous dit de faire écrire à Claude. Il est
là, testé.

```bash
# Top 10 des vidéos les plus vues d'une chaîne
python3 scripts/yt-transcripts.py "https://www.youtube.com/@chaine" --top 10

# Une playlist entière
python3 scripts/yt-transcripts.py "https://youtube.com/playlist?list=XXX" --top 0

# Des URLs précises, ou un fichier texte (une URL par ligne)
python3 scripts/yt-transcripts.py "https://youtu.be/A" "https://youtu.be/B"
python3 scripts/yt-transcripts.py mes-urls.txt --out faceless/refs
```

| Flag | Effet | Défaut |
|---|---|---|
| `--top N` | garder les N plus vues (`0` = toutes) | `10` |
| `--limit N` | vidéos scannées par source | `100` |
| `--lang` | langues de sous-titres, par préférence | `fr,en` |
| `--out DIR` | dossier de sortie | `transcripts/` |
| `--every N` | un timecode toutes les N secondes (`0` = texte continu) | `30` |

**Dépendance : `yt-dlp` seul.** Les sous-titres sont récupérés en VTT natif, donc
ffmpeg n'est pas nécessaire ici — contrairement à la skill `/watch`.

```bash
pipx install yt-dlp     # ou: brew install yt-dlp
```

Sortie : un `.md` par vidéo (titre, URL, vues, durée, langue, transcription
horodatée), plus `index.md` et `index.json`.

### Pourquoi pas un outil web

La méthode d'origine renvoie vers un extracteur en ligne, une vidéo à la fois. Le
script fait le lot, trie par nombre de vues, et sort un corpus exploitable
directement — ce qui change la nature de l'analyse à l'étape suivante.

### Limites connues

- **Pas de sous-titres, pas de transcription.** Le script signale les vidéos ignorées.
  Pour celles-là, la skill `/watch` sait transcrire via Whisper (et extraire les
  frames).
- **Le tri par vues dépend de ce que YouTube expose** en mode `--flat-playlist`. Quand
  le compteur manque sur une partie des vidéos, le script prévient que le classement
  est partiel plutôt que de les jeter silencieusement.
- **Chemin réseau non testé dans l'environnement cloud** : YouTube y est bloqué par la
  politique egress. La logique de parsing est couverte par 22 tests
  (`tests/test_yt_transcripts.py`) ; la collecte réelle a été écrite mais pas exécutée
  ici. Testez-la en local au premier usage.

---

## 3. Extraire le pattern — agent `analyse`

Sur le corpus, pas vidéo par vidéo. Sortie attendue : familles de hooks comptées,
structure type, rythme, relances de rétention, CTA.

**Une vidéo qui marche peut marcher par accident. Un pattern qui se répète sur dix
vidéos et deux chaînes est un pattern.** C'est la principale différence entre cette
implémentation et la méthode d'origine, qui analyse une seule vidéo.

---

## 4. Écrire — agent `redaction` (ou skill `script-b2b`)

Même squelette, contenu entièrement propre.

### Garde-fou anti-copie

Quatre points vérifiés avant qu'un script parte en production :

1. Aucune suite de plus de 6 mots reprise d'une source (vérifiable mécaniquement).
2. Aucun exemple ni chiffre repris sans être re-sourcé indépendamment.
3. L'enchaînement des idées diffère — même structure, pas même suite d'arguments.
4. Titre et miniature ne sont pas des variantes d'une vidéo source.

Ce n'est pas de la prudence excessive. Trois risques distincts : le droit d'auteur
(l'expression est protégée, l'idée ne l'est pas), les règles de « contenu réutilisé »
qui bloquent la monétisation, et le fait qu'une copie diluée performe moins bien que
son original.

---

## 5. Générer les visuels — Higgsfield MCP

Une trentaine de modèles image et vidéo (Seedance, Kling, Veo…) via une connexion.

### Vérifier avant de configurer

Si les outils `mcp__Higgsfield__*` sont déjà disponibles dans la session, **le
connecteur est branché** — rien à faire. C'était le cas au moment d'écrire ce
document.

### Configuration (claude.ai)

1. Réglages → Connecteurs
2. `+` → « Ajouter un connecteur personnalisé »
3. Nom : `Higgsfield` — adresse : `https://mcp.higgsfield.ai/mcp`
4. « Connecter » → redirection vers Higgsfield → autoriser l'accès

### Configuration (ChatGPT)

Réglages → Apps et connecteurs → nouveau connecteur MCP →
`https://mcp.higgsfield.ai/mcp` → authentification OAuth → autoriser.

### Méthode

1. Découper le script en plans (1 plan = 1 idée = 1 visuel).
2. Écrire tous les prompts **avant** de générer, et les faire valider.
3. Fixer une direction artistique et la répéter sur toute la série — c'est ce qui
   rend une chaîne reconnaissable.
4. Générer par lot plutôt qu'un appel par visuel.
5. Regarder les sorties avant de monter.

Format cible : **1080×1920**.

> Les codes promo et crédits gratuits circulant avec ce genre de méthode sont
> généralement limités dans le temps. Vérifiez les conditions et la tarification
> courante sur le site avant de vous engager.

---

## 6. Monter — agent `montage`

Découpe, assemblage, sous-titres incrustés, rendu 1080×1920, contrôle `ffprobe` +
lecture de frames.

En faceless, les **sous-titres sont obligatoires** : une grande partie de l'audience
regarde sans le son. Le hook doit tomber dans les 3 premières secondes, à l'image
**et** en texte.

---

## Arborescence de travail

```
faceless/
├── niche.md              # niche retenue, angle, test des 50 vidéos
├── refs/                 # transcriptions collectées (+ index.md)
├── pattern.md            # le mécanisme extrait du corpus
├── scripts/              # scripts originaux, 3 hooks chacun
├── visuels/              # générations Higgsfield
└── rendus/               # vidéos finales
```

`faceless/` et `transcripts/` sont dans le `.gitignore` : contenu tiers et fichiers
lourds. Retirez la ligne pour les versionner.

---

## Vérification

```bash
python3 -m pytest tests/ -q                 # 22 tests de parsing
python3 scripts/yt-transcripts.py --help
yt-dlp --version
```
