# NEXA — Landing page « E-book : +50 outils IA à connaître en 2026 »

Landing page de type *lead magnet* (téléchargement d'un e-book gratuit contre e-mail),
adaptée aux couleurs et au positionnement NEXA à partir de la structure de la page Liora.

> **Contenu original** : les textes ont été réécrits à la marque NEXA (pas de copie mot pour mot).
> Les éléments que je ne connaissais pas sont des **placeholders** à remplacer (voir plus bas).

## 📁 Fichiers

| Fichier | Rôle |
|---|---|
| `page-complete.html` | Page entière assemblée — **pour prévisualiser** dans un navigateur |
| `blocs-webflow/00-styles.html` | **CSS partagé** — à coller UNE fois (head de page ou 1er Embed) |
| `blocs-webflow/01-hero.html` | Section Hero (fond violet + liste d'atouts + bouton) |
| `blocs-webflow/02-decouvrir.html` | « Ce que vous allez découvrir » (3 cartes) |
| `blocs-webflow/03-auteurs.html` | « À propos des auteurs » |
| `blocs-webflow/04-formations.html` | Bandeau CTA « Nos formations IA » |
| `blocs-webflow/05-temoignages.html` | Témoignages / notes |
| `blocs-webflow/06-formulaire.html` | Formulaire de capture (ancre `#nx-form`) |
| `blocs-webflow/07-footer.html` | Contact / footer |

## 🚀 Intégration dans Webflow (format Embed découpé)

1. **Le style d'abord.** Ouvre `00-styles.html`, copie tout le bloc `<style>…</style>` et colle-le dans :
   **Webflow → Page Settings → Custom Code → « Inside `<head>` tag »**.
   (Alternative : un composant **Embed** placé tout en haut de la page.)
2. **Les sections ensuite.** Pour chaque fichier `01` → `07`, glisse un composant
   **Embed** (`Add panel → Components → Embed`) dans la page, dans l'ordre, et colle le contenu du fichier.
   > La limite d'un Embed Webflow est de 50 000 caractères : chaque bloc est bien en dessous.
3. **Publie** et vérifie le rendu mobile (le CSS est déjà responsive, breakpoint à 860 px).

Astuce : tu peux aussi coller `page-complete.html` dans un seul gros Embed, mais le découpage
facilite les retouches section par section directement dans Webflow.

## ✏️ Placeholders à remplacer

- **Logos d'outils** (bloc 02) : les pastilles `nx-logo-chip` (MJ, CV, GPT…) → remplace par de vraies `<img>`.
- **Photo équipe** (bloc 03) : la `div.nx-photo` → remplace par `<img class="nx-photo" src="…" alt="…">`.
- **URL des boutons** : « Postuler », « En savoir plus », « Voir nos formations », liens footer (`href="#"`).
- **Témoignages** (bloc 05) : scores, nombre d'avis `[nb]` et citations `[Témoignage à compléter]`.
- **Contact** (bloc 07) : `[Adresse NEXA]`, `[Téléphone NEXA]`, e-mail, mentions RNCP/Qualiopi.
- **Formulaire** (bloc 06) : `action="REMPLACER_PAR_URL_HUBSPOT"` (voir ci-dessous).

## 🔗 Connexion du formulaire à HubSpot

Deux options :

- **Recommandé — HubSpot Forms embed** : crée le formulaire dans HubSpot, récupère son
  code d'intégration (script JS) et remplace tout le `<form>…</form>` du bloc 06 par ce code.
  Tu gardes le tracking, la validation et les workflows HubSpot natifs.
- **Formulaire HTML custom** : garde le `<form>` fourni et mets dans `action="…"` l'URL de ton
  endpoint (Forms API / workflow / webhook). Les champs sont déjà nommés `firstname`, `lastname`, `email`.

## 🎨 Charte

Couleurs définies en variables CSS en haut de `00-styles.html` (`--nx-violet`, etc.).
Base violet `#4B0082` (reprise de ton repo). Modifie ces variables pour coller exactement à ta charte,
et ajuste `font-family` si ta police Webflow diffère (Poppins par défaut).
