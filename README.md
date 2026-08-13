# Vie etudiante NEXA 2026-2027

Landing page des temps forts de la vie etudiante NEXA. Vite + React + TypeScript + Tailwind + Framer Motion. Aucun backend, tout est statique.

---

## Ce que tu veux surement faire : ouvrir les inscriptions d'un evenement

Tu n'as **qu'un seul fichier a modifier** :

```
src/data/events.ts
```

Tu n'as **jamais besoin de toucher au code** des composants.

### Etape par etape

1. Ouvre `src/data/events.ts`.
2. Trouve l'evenement concerne grace a son `id` (ex. `nex-leader`, `nexi-play`...).
3. Sur cet evenement, tu modifies **2 lignes** :

   - **le lien d'inscription** : soit `formEmbedUrl`, soit `formLinkUrl` (voir ci-dessous) ;
   - **le statut** : `statut`.

4. Enregistre. Le site se met a jour tout seul au prochain deploiement.

### `formEmbedUrl` ou `formLinkUrl` ? La difference

| Champ           | Ce que ca fait                                                             | Quand l'utiliser                                              |
| --------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `formEmbedUrl`  | Le formulaire s'affiche **directement dans une fenetre** sur la page.      | Tu as un lien de formulaire **integrable** (Google Forms « incorporer », Tally, HubSpot embed...). |
| `formLinkUrl`   | Un bouton violet ouvre le formulaire **dans un nouvel onglet**.            | Tu as juste un lien classique a partager.                    |

> Renseigne **l'un OU l'autre**, pas besoin des deux. Si tu mets les deux, le formulaire integre (`formEmbedUrl`) est prioritaire.

### Le champ `statut`

| Valeur       | Effet sur le bouton                                          |
| ------------ | ----------------------------------------------------------- |
| `'ouvert'`   | Bouton plein violet **« Je m'inscris »**                    |
| `'selection'`| Bouton contour cyan **« Je candidate »** (dossier/entretien)|
| `'bientot'`  | Bouton grise **« Inscriptions bientot ouvertes »**          |
| `'ferme'`    | Bouton grise **« Inscriptions closes »**                    |

### Exemple concret

Avant (inscriptions pas encore ouvertes) :

```ts
statut: 'bientot',
formEmbedUrl: null,
formLinkUrl: null,
```

Apres (inscriptions ouvertes avec un lien classique) :

```ts
statut: 'ouvert',
formEmbedUrl: null,
formLinkUrl: 'https://forms.gle/xxxxxxxx',
```

Apres (inscriptions ouvertes avec un formulaire integre) :

```ts
statut: 'ouvert',
formEmbedUrl: 'https://docs.google.com/forms/d/e/xxxx/viewform?embedded=true',
formLinkUrl: null,
```

### Garde-fou (important)

Tant que **les deux liens sont a `null`**, le bouton reste **desactive automatiquement**, meme si tu mets `statut: 'ouvert'` par erreur. Impossible d'avoir un bouton qui ne mene nulle part.

---

## Les visuels

Les images des evenements vont dans `public/img/` au format `.webp`, en 16:9 :

```
public/img/nex-leader.webp
public/img/nex-champ.webp
public/img/nex-lab.webp
public/img/nex-in.webp
public/img/datathon.webp
public/img/cluedo-geant.webp
public/img/gaming-night.webp
public/img/octobre-rose.webp
public/img/nexi-play.webp
public/img/business-game.webp   (a produire)
public/img/hackathon.webp       (a produire)
public/img/og-cover.jpg         (image de partage reseaux sociaux)
```

Si un fichier est absent, un **placeholder violet propre** avec le titre s'affiche a la place : la grille ne casse jamais. C'est le cas prevu pour `business-game` et `hackathon` tant que leurs visuels ne sont pas produits.

---

## Lancer le projet

```bash
npm install     # une seule fois
npm run dev     # developpement (http://localhost:5173)
npm run build   # build de production dans dist/
npm run preview # previsualiser le build
```

Deploiement Netlify : la config est dans `netlify.toml` (build `npm run build`, dossier `dist`).

---

## Reglages ponctuels (pour un dev)

- **Rendre la page visible sur Google** : dans `index.html`, supprimer la balise `<meta name="robots" content="noindex, nofollow" />`.
- **Activer le suivi GTM** : dans `index.html`, de-commenter le bloc Google Tag Manager et remplacer `GTM-XXXXXXX` par l'identifiant du conteneur. Le `dataLayer` est deja alimente par le code (`src/lib/analytics.ts`).
- **Brancher la video teaser** : dans `src/components/VideoSection.tsx`, renseigner `VIDEO_ID` avec l'identifiant YouTube.
- **Modifier un libelle de bouton** : ajouter un champ optionnel `ctaLabel: 'Mon texte'` sur l'evenement dans `events.ts` (deja utilise par NEX IN et NEXI'PLAY).
