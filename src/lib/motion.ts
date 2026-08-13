import type { Variants } from 'framer-motion';

// Variants Framer Motion partages.
// prefers-reduced-motion est gere via le hook useReducedMotion de Framer
// directement dans les composants : quand il est actif, on passe des variants
// "plats" (fade simple, pas de translation, pas de spring).

export const REVEAL_OFFSET = 24; // px de translation au scroll reveal

export const sectionReveal: Variants = {
  hidden: { opacity: 0, y: REVEAL_OFFSET },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  },
};

export const sectionRevealReduced: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
};

// Conteneur qui applique un stagger de 60ms entre ses enfants (cards).
export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.06 },
  },
};

export const cardItem: Variants = {
  hidden: { opacity: 0, y: REVEAL_OFFSET },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.22, 1, 0.36, 1] },
  },
};

export const cardItemReduced: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.25 } },
};

// Seuil d'apparition commun (15% visible).
export const VIEWPORT_ONCE = { once: true, amount: 0.15 } as const;
