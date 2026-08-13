import type { NexaEvent } from '../data/events';

// Etat visuel/fonctionnel du bouton d'inscription, calcule a partir des donnees.
// Voir le tableau du brief (section 8). Reutilise par la card ET la modale.

export type CtaVariant = 'solid' | 'outline' | 'disabled';

export interface CtaState {
  label: string;
  variant: CtaVariant;
  /** true = le bouton declenche une action (ouvre la modale). */
  actionable: boolean;
  /** true = affiche l'attribut aria-disabled + title explicatif. */
  disabled: boolean;
  /** Message d'explication pour l'attribut title des boutons desactives. */
  title?: string;
}

/** Une URL d'inscription est-elle renseignee (embed OU lien) ? */
export function hasRegistrationUrl(event: NexaEvent): boolean {
  return Boolean(event.formEmbedUrl || event.formLinkUrl);
}

export function getCtaState(event: NexaEvent): CtaState {
  const hasUrl = hasRegistrationUrl(event);

  // Garde-fou non contournable : sans URL, le bouton est desactive
  // meme si le statut vaut 'ouvert'. Evite tout bouton mort.
  if (!hasUrl) {
    return {
      label: 'Inscriptions bientot ouvertes',
      variant: 'disabled',
      actionable: false,
      disabled: true,
      title: "Le lien d'inscription n'est pas encore disponible. Reviens bientot.",
    };
  }

  if (event.statut === 'ferme') {
    return {
      label: 'Inscriptions closes',
      variant: 'disabled',
      actionable: false,
      disabled: true,
      title: 'Les inscriptions pour cet evenement sont terminees.',
    };
  }

  if (event.statut === 'selection') {
    return {
      label: event.ctaLabel ?? 'Je candidate',
      variant: 'outline',
      actionable: true,
      disabled: false,
    };
  }

  if (event.statut === 'ouvert') {
    return {
      label: event.ctaLabel ?? "Je m'inscris",
      variant: 'solid',
      actionable: true,
      disabled: false,
    };
  }

  // statut === 'bientot' mais une URL est deja presente :
  // on considere l'inscription comme ouverte (le contenu prime sur le libelle).
  return {
    label: event.ctaLabel ?? "Je m'inscris",
    variant: 'solid',
    actionable: true,
    disabled: false,
  };
}
