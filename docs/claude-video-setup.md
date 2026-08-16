# Setup vidéo pour Claude Code

Trois briques indépendantes, installées dans ce dépôt : la skill `/watch`, un accès
Gemini pour YouTube, et quatre agents de production de contenu.

---

## 1. Skill `/watch`

Donne à Claude la capacité de **regarder** une vidéo : téléchargement, extraction
de frames, transcription horodatée, puis lecture des images par Claude.

Source : [`bradautomates/claude-video`](https://github.com/bradautomates/claude-video)
(MIT, Brad Bonanno). Copie vendorée verbatim dans `.claude/skills/watch/`.

### Pourquoi vendorée plutôt qu'installée en plugin

L'install recommandée en local est :

```
/plugin marketplace add bradautomates/claude-video
/plugin install watch@claude-video
```

Mais `/plugin` n'est pas disponible dans les sessions Claude Code sur le web. En
copiant la skill dans `.claude/skills/`, elle est versionnée avec le dépôt et
fonctionne partout : terminal, web, mobile, sur toute machine qui clone le repo.

Contrepartie : **pas de mise à jour automatique**. Pour resynchroniser :

```bash
git clone --depth 1 https://github.com/bradautomates/claude-video /tmp/cv
rm -rf .claude/skills/watch && cp -r /tmp/cv/skills/watch .claude/skills/watch
cp /tmp/cv/LICENSE .claude/skills/watch/LICENSE
```

Version vendorée : voir le champ `version` dans `.claude/skills/watch/SKILL.md`.

### Dépendances

`yt-dlp` et `ffmpeg` doivent être sur le PATH. Au premier `/watch`, la skill lance
`scripts/setup.py` qui les installe (macOS/Homebrew) ou affiche les commandes
exactes (Linux/Windows).

```bash
# macOS
brew install ffmpeg yt-dlp
# Debian / Ubuntu
sudo apt install ffmpeg && pipx install yt-dlp
```

### Usage

```
/watch https://youtu.be/XXXX que se passe-t-il à 30 secondes ?
/watch ~/Movies/rush.mov où est-ce que l'UI casse ?
/watch "$URL" --start 2:15 --end 2:45
```

Réglages utiles :

| Flag | Effet |
|---|---|
| `--detail transcript` | transcription seule, aucune frame — le plus économique |
| `--detail efficient` | keyframes rapides, plafond 50 frames |
| `--detail balanced` | frames scène par scène, plafond 100 (défaut) |
| `--detail token-burner` | scène par scène, sans plafond |
| `--start` / `--end` | focus sur une portion — bien plus dense qu'un scan large |
| `--resolution 1024` | pour lire du texte à l'écran (slides, terminal, code) |

Au-delà de ~10 minutes, les modes plafonnés deviennent clairsemés : mieux vaut une
passe `--detail transcript` pour repérer, puis une passe ciblée `--start/--end`.

### Clé Whisper : souvent inutile

`/watch` récupère d'abord les **sous-titres natifs** via yt-dlp — gratuit, et ça
couvre la majorité des vidéos YouTube publiques. Whisper n'est appelé qu'en
secours, quand il n'y a aucune piste de sous-titres : fichiers locaux, TikTok,
certains Vimeo.

Dans ce cas, une clé [Groq](https://console.groq.com/keys) (préférée) ou
[OpenAI](https://platform.openai.com/api-keys) dans `~/.config/watch/.env`. Sinon,
`--no-whisper` donne un résultat frames seules.

### Ce qui sort du poste

D'après le SKILL.md : seul l'**audio extrait** part vers `api.groq.com` ou
`api.openai.com`, et uniquement quand Whisper est déclenché. La vidéo n'est jamais
uploadée. `yt-dlp` ne fait que des requêtes publiques, sans login ni cookies.
Vérification faite sur les scripts vendorés : aucun autre endpoint réseau.

---

## 2. Gemini — lecture native de YouTube

**Ce n'est pas une skill.** C'est une clé API, et un script qui l'utilise :
`scripts/gemini-video.py`.

Différence avec `/watch` :

| | `/watch` | `gemini-video.py` |
|---|---|---|
| Sources | YouTube, TikTok, Vimeo, X, fichiers locaux | YouTube uniquement |
| Fonctionnement | télécharge, échantillonne des frames, transcrit | envoie l'URL, Gemini lit nativement |
| Durée confortable | < 10 min (au-delà : passes ciblées) | plusieurs heures en un appel |
| Qui analyse | **Claude**, qui voit les frames | **Gemini**, qui rend un texte |
| Coût | tokens image dans ton contexte | quota Gemini (offre gratuite généreuse) |

Les deux sont complémentaires : Gemini pour dégrossir une longue vidéo YouTube,
`/watch` quand Claude doit voir lui-même le détail visuel d'un moment précis.

### Installation

1. Clé gratuite sur [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. `cp .env.example .env` puis renseigne `GEMINI_API_KEY`

```bash
python3 scripts/gemini-video.py --list-models
python3 scripts/gemini-video.py "https://youtu.be/XXXX" "Résume les 3 idées clés"
python3 scripts/gemini-video.py "$URL" "Que montre-t-il ?" --start 2:15 --end 2:45
```

Le script est en stdlib pure, sans dépendance. Il lit `GEMINI_API_KEY` depuis
l'environnement, puis `.env`, puis `~/.config/watch/.env`.

`--list-models` interroge l'API pour les noms de modèles valides — le défaut
`gemini-2.5-flash` peut vieillir, cette commande donne la liste à jour.

> **Note pour les sessions Claude Code sur le web** :
> `generativelanguage.googleapis.com` n'est pas dans l'allowlist réseau par défaut.
> Le script fonctionne en local sans rien faire ; pour l'utiliser depuis une session
> cloud, il faut passer l'environnement en **Custom** et ajouter ce domaine
> (voir `docs/reseau-egress.md`).

---

## 3. Agents

Quatre agents dans `.claude/agents/`, invocables via `/agents` ou en langage
naturel. Ils ne sont pas des skills : ce sont des sous-agents avec leur propre
contexte et leur propre jeu d'outils.

| Agent | Rôle | Outils |
|---|---|---|
| `veille` | sort des sujets de contenu sourcés et datés | WebSearch, WebFetch |
| `analyse` | décortique un contenu existant (hook, structure, preuves, CTA) | `watch`, WebFetch |
| `redaction` | écrit le livrable fini (script, post, page, email) | `script-b2b`, fichiers |
| `montage` | rush → Reel 1080×1920 sous-titré | ffmpeg, `watch` |

Chaîne complète :

```
veille  →  analyse  →  redaction  →  montage
sujets     structure   script       vidéo finie
```

Chaque agent est autonome : on peut entrer par n'importe quelle étape.

### `montage` en détail

C'est l'agent le plus lourd. Il enchaîne :

1. transcription horodatée via `/watch --detail transcript`
2. repérage des blancs, faux départs, et du meilleur hook
3. découpe et concaténation ffmpeg — **soumise à validation** avant rendu
4. recadrage 1080×1920 (crop centré, ou fond flouté)
5. sous-titres `.srt` incrustés, remontés à `MarginV=180` pour passer au-dessus
   de l'UI TikTok/Reels
6. inserts et B-roll sur intervalle
7. contrôle `ffprobe` + lecture de 3 frames extraites avant livraison

Les rushes sources ne sont jamais modifiés en place.

---

## Vérification rapide

```bash
ls .claude/skills/watch/SKILL.md .claude/agents/     # skill + agents en place
python3 scripts/gemini-video.py --help               # script exécutable
ffmpeg -version && yt-dlp --version                  # dépendances /watch
```

---

## Sur la vidéo d'origine

Ce setup vient d'un Reel Instagram. Deux écarts constatés entre ce qui y est
annoncé et le dépôt réel :

- La vidéo présente la clé Gemini comme le moteur de transcription. En réalité
  `/watch` n'utilise **pas** Gemini : sous-titres yt-dlp d'abord, puis Whisper via
  Groq/OpenAI. Gemini est une capacité séparée — d'où le script dédié.
- Le « guide complet de James Hetman » cité dans la vidéo n'a pas été vérifié :
  aucun lien n'a pu être récupéré (Instagram est inaccessible depuis cette session).
