// ─────────────────────────────────────────────────────────────────────────────
// FICHIER A EDITER AU FIL DE L'ANNEE.
// Pour ouvrir les inscriptions d'un evenement : voir le README.
// En resume, sur l'evenement concerne :
//   1. renseigner formEmbedUrl (formulaire integre) OU formLinkUrl (lien externe)
//   2. passer statut a 'ouvert' (ou 'selection' pour une candidature)
// Tant que les deux URL sont null, le bouton reste desactive automatiquement.
// ─────────────────────────────────────────────────────────────────────────────

export type EventStatus = 'ouvert' | 'selection' | 'bientot' | 'ferme';

export type EventTheme =
  | 'competitions'
  | 'leadership'
  | 'entrepreneuriat'
  | 'engagement'
  | 'challenges'
  | 'soirees';

export interface NexaEvent {
  id: string;
  titre: string;
  accroche: string;
  descriptionCard: string;
  descriptionModale: string;
  theme: EventTheme;
  visuel: string; // nom de fichier dans /public/img
  alt: string;
  campus: string[]; // ['tous'] = tous les campus
  dateAffichee: string | null;
  infos: string[];
  badge: string | null;
  statut: EventStatus;
  formEmbedUrl: string | null; // formulaire a integrer en iframe dans la modale
  formLinkUrl: string | null; // OU lien externe ouvert dans un nouvel onglet
  ctaLabel?: string; // surcharge optionnelle du libelle du bouton
}

// Thematiques : libelle de filtre + couleur du tag.
export type ThemeTag = 'violet' | 'violet-dark' | 'cyan' | 'orange';
export type ThemeMeta = { label: string; tag: ThemeTag };

export const THEMES: Record<EventTheme, ThemeMeta> = {
  competitions: { label: 'Competitions', tag: 'violet' },
  leadership: { label: 'Leadership & eloquence', tag: 'violet-dark' },
  entrepreneuriat: { label: 'Entrepreneuriat', tag: 'orange' },
  engagement: { label: 'Engagement', tag: 'cyan' },
  challenges: { label: 'Challenges & hackathons', tag: 'violet' },
  soirees: { label: 'Soirees & gaming', tag: 'orange' },
};

// Ordre d'affichage des filtres thematiques.
export const THEME_ORDER: EventTheme[] = [
  'competitions',
  'leadership',
  'entrepreneuriat',
  'engagement',
  'challenges',
  'soirees',
];

// Liste des campus pour le filtre secondaire.
// Un evenement dont campus vaut ['tous'] correspond a n'importe quel campus.
export const CAMPUS = ['Paris', 'Lyon', 'Lille', 'Bordeaux', 'Nantes', 'A distance'] as const;

export const events: NexaEvent[] = [
  {
    id: 'nex-leader',
    titre: 'NEX LEADER',
    accroche: 'Prends la parole. Fais-toi entendre.',
    descriptionCard:
      "Un concours d'eloquence ouvert a tous, sur tous les campus. Coaching en visio par un pro de la prise de parole, hors heures de formation. Demi-finale sur ton campus, finale nationale a Lyon.",
    descriptionModale:
      "NEX LEADER, c'est le rendez-vous de celles et ceux qui veulent apprendre a convaincre. Tu t'inscris, tu es coache individuellement en visio par un professionnel de l'eloquence, en dehors de tes heures de formation. Tu passes d'abord une demi-finale sur ton campus, puis les meilleurs se retrouvent en finale nationale a Lyon, la ou s'est jouee l'edition 2026. L'ecole prend en charge tes frais de deplacement pour la finale. Aucune experience requise, juste l'envie de te lancer.",
    theme: 'leadership',
    visuel: 'nex-leader.webp',
    alt: "Nexi de dos sur la scene d'un auditorium, face a un micro",
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Ouvert a tous', 'Coaching pro en visio', 'Finale nationale a Lyon'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'nex-champ',
    titre: 'NEX CHAMP',
    accroche: 'Capture the flag, en vrai.',
    descriptionCard:
      'Des competitions cyber nationales inter-ecoles, en ligne ou en presentiel. Tu representes NEXA face aux autres ecoles tech.',
    descriptionModale:
      "NEX CHAMP, c'est l'equipe qui porte les couleurs de NEXA sur les competitions cyber nationales. Des CTF inter-ecoles, en ligne ou sur place, face a des equipes venues de toute la France. L'acces se fait sur inscription puis entretien de motivation, parce que representer l'ecole demande de l'engagement. Reserve aux Masteres CYB. Les frais de deplacement sont pris en charge.",
    theme: 'competitions',
    visuel: 'nex-champ.webp',
    alt: 'Nexi de dos face a un ecran CRT affichant du code, dans une salle neon',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Reserve aux Masteres CYB', 'Inscription + entretien', 'Frais de deplacement pris en charge'],
    badge: null,
    statut: 'selection',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'nex-lab',
    titre: 'NEX LAB',
    accroche: "Ton idee merite mieux qu'une note dans ton telephone.",
    descriptionCard:
      "Le Cercle de l'innovation. Tu developpes ton projet de start-up avec un coaching pro, et tu le defends en finale nationale a Paris.",
    descriptionModale:
      "NEX LAB, c'est le Cercle de l'innovation de NEXA. Tu arrives avec une idee, meme floue, et tu repars avec un projet structure. Coaching en visio par un professionnel de la creation d'entreprise, en dehors de tes heures de formation. Le point d'orgue, c'est la finale nationale sur le campus de Paris : un pitch devant jury, facon « Qui veut etre mon associe ». Frais de deplacement pris en charge pour la finale.",
    theme: 'entrepreneuriat',
    visuel: 'nex-lab.webp',
    alt: 'Nexi avec une cravate orange dans un espace de coworking, sous une ampoule',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Ouvert a tous', 'Coaching pro en visio', 'Finale nationale a Paris'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'nex-in',
    titre: 'NEX IN',
    accroche: 'Laisse une trace sur ton campus.',
    descriptionCard:
      'Tu concois et tu realises une action inclusive ou professionnelle sur ton campus. Obligatoire pour les Masteres 1 et 2, note au bulletin.',
    descriptionModale:
      "NEX IN, c'est ton projet d'engagement. Tu identifies un besoin sur ton campus, tu montes une action inclusive ou professionnelle, et tu la menes jusqu'au bout. Sensibilisation, evenement, initiative solidaire, tout est possible tant que ca sert la communaute. C'est obligatoire pour tous les Masteres 1 et 2, et une note est integree a ton bulletin d'evaluation. Beaucoup d'etudiants en font ensuite un vrai sujet d'entretien.",
    theme: 'engagement',
    visuel: 'nex-in.webp',
    alt: 'Nexi portant une echarpe cyan dans un couloir de campus lumineux',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Obligatoire M1 et M2', 'Action sur ton campus', 'Note au bulletin'],
    badge: 'Obligatoire M1 & M2',
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
    ctaLabel: 'Je depose mon projet',
  },
  {
    id: 'business-game',
    titre: 'BUSINESS GAME',
    accroche: '48h pour faire tourner une boite.',
    descriptionCard:
      'En equipe, tu pilotes une entreprise digitale sur un simulateur. Strategie, budget, arbitrages. Le classement tombe a la fin.',
    descriptionModale:
      "Le Business Game Digital te met aux commandes d'une entreprise. En equipe, tu prends les decisions : investissement, recrutement, prix, communication. Chaque tour, le simulateur calcule les consequences et le classement bouge. C'est le meilleur moyen de comprendre ce que veut dire « arbitrer » quand le budget ne suit pas. Ouvert aux B2 et B3.",
    theme: 'challenges',
    // Visuel a produire : un placeholder violet est genere automatiquement si le fichier est absent.
    visuel: 'business-game.webp',
    alt: 'Visuel Business Game Digital',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['En equipe', 'B2 et B3', 'Classement final'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'hackathon',
    titre: 'HACKATHON',
    accroche: 'Un sujet, une nuit, un proto.',
    descriptionCard:
      'Un brief le matin, un prototype fonctionnel devant le jury a la fin. Toutes les filieres melangees.',
    descriptionModale:
      "Le Hackathon NEXA, c'est le format le plus intense de l'annee. Un sujet devoile le matin, des equipes pluridisciplinaires, et un prototype a presenter au jury a la fin. Dev, design, data, cyber, marketing : c'est justement le melange qui fait la difference. Tu ne codes pas ? Tu es quand meme indispensable. Prix a la cle.",
    theme: 'challenges',
    // Visuel a produire : un placeholder violet est genere automatiquement si le fichier est absent.
    visuel: 'hackathon.webp',
    alt: 'Visuel Hackathon NEXA',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Equipes pluridisciplinaires', 'Jury de pros', 'Prix a la cle'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'datathon',
    titre: 'DATATHON',
    accroche: 'Un jeu de donnees. Une reponse a trouver.',
    descriptionCard:
      'Tu explores un dataset reel, tu construis ton analyse et tu defends tes conclusions devant un jury.',
    descriptionModale:
      "Le Datathon te confronte a un vrai jeu de donnees, avec ses trous, ses doublons et ses pieges. En equipe, tu nettoies, tu explores, tu modelises, puis tu defends tes conclusions devant un jury. Ce qui compte n'est pas seulement la performance du modele, mais ta capacite a raconter ce que disent les donnees. Le terrain ideal si la data est ton truc.",
    theme: 'challenges',
    visuel: 'datathon.webp',
    alt: 'Nexi de dos avec une echarpe, face a un mur d\'ecrans de dataviz',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Dataset reel', 'En equipe', 'Restitution devant jury'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'cluedo-geant',
    titre: 'CLUEDO GEANT',
    accroche: 'Il y a un coupable dans ton campus.',
    descriptionCard:
      'Le campus se transforme en scene de crime pour la soiree Halloween. Indices, interrogatoires, fausses pistes.',
    descriptionModale:
      "Chaque annee, la soiree Halloween transforme le campus en Cluedo grandeur nature. Des indices caches dans les salles, des suspects a interroger, des fausses pistes bien placees, et une equipe qui trouve le coupable avant les autres. Deguisement vivement conseille. C'est la soiree que personne ne rate, alors les places partent vite.",
    theme: 'soirees',
    visuel: 'cluedo-geant.webp',
    alt: 'Nexi en tenue de detective dans un couloir de campus decore pour Halloween',
    campus: ['tous'],
    dateAffichee: 'Octobre 2026',
    infos: ['Tous campus', 'Octobre 2026', 'Places limitees'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'gaming-night',
    titre: 'GAMING NIGHT',
    accroche: 'Manettes, ecrans, trash talk.',
    descriptionCard:
      'Tournois, ecrans geants et defis entre promos. Que tu sois no-life ou grand debutant.',
    descriptionModale:
      "La Gaming Night, c'est une soiree entiere autour du jeu. Tournois par equipes, ecrans geants, retro gaming et defis entre promos. Le niveau n'a aucune importance : il y a toujours une partie pour toi, et souvent une revanche a prendre. Entree libre, mais sur inscription pour qu'on prevoie assez de manettes.",
    theme: 'soirees',
    visuel: 'gaming-night.webp',
    alt: 'Nexi avec des lunettes pixel sur un canape dans une salle de jeu neon',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Tous campus', 'Tournois par equipes', 'Sur inscription'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'octobre-rose',
    titre: 'OCTOBRE ROSE',
    accroche: 'On se mobilise, tous campus confondus.',
    descriptionCard:
      "Un mois d'actions de sensibilisation au depistage, portees par les etudiants sur chaque campus.",
    descriptionModale:
      "Pendant tout le mois d'octobre, les campus NEXA se mobilisent pour la sensibilisation au depistage du cancer du sein. Stands, collectes, actions de communication, marches : les initiatives viennent des etudiants. Tu peux rejoindre une action existante ou proposer la tienne. Et c'est un excellent support pour ton projet NEX IN si tu es en Mastere.",
    theme: 'engagement',
    visuel: 'octobre-rose.webp',
    alt: 'Nexi portant un ruban rose dans une allee de cerisiers en fleurs',
    campus: ['tous'],
    dateAffichee: 'Octobre 2026',
    infos: ['Tous campus', 'Ouvert a tous', 'Valorisable en NEX IN'],
    badge: null,
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
  },
  {
    id: 'nexi-play',
    titre: "NEXI'PLAY",
    accroche: 'Le nouveau terrain de jeu de toute la communaute.',
    descriptionCard:
      "7 mini-jeux d'arcade autour du code, de la data et de l'alternance, avec Nexi en heros. Classement national en temps reel.",
    descriptionModale:
      "Nexi'Play, c'est la grosse nouveaute de l'annee. Sept mini-jeux d'arcade revisites autour du code, de la data et de l'alternance, avec Nexi dans le role principal. Chaque partie alimente ton Score Nexi, et ton score fait monter ton campus au classement national en temps reel. Les compteurs sont remis a zero tous les mois : tout le monde repart a egalite, et le meilleur joueur du mois repart avec des goodies NEXA.",
    theme: 'soirees',
    visuel: 'nexi-play.webp',
    alt: 'Nexi en saut avec une couronne dans une salle d\'arcade neon',
    campus: ['tous'],
    dateAffichee: null,
    infos: ['Tous campus', 'Classement national', 'Reset mensuel'],
    badge: 'Nouveaute',
    statut: 'bientot',
    formEmbedUrl: null,
    formLinkUrl: null,
    ctaLabel: 'Je joue maintenant',
  },
];
