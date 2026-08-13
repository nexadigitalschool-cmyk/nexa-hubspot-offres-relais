import { THEMES, type EventTheme, type ThemeTag as ThemeTagColor } from '../../data/events';

interface Props {
  theme: EventTheme;
  /** true sur fond sombre (modale/hero), false sur fond clair (card). */
  onDark?: boolean;
}

// Le tag thematique : une pastille de couleur (decorative) + le libelle.
// La pastille evite le probleme de contraste du cyan sur blanc :
// c'est le texte, toujours en ink ou blanc, qui porte la lisibilite.
const DOT: Record<ThemeTagColor, string> = {
  violet: 'bg-violet',
  'violet-dark': 'bg-violet-dark',
  cyan: 'bg-cyan',
  orange: 'bg-orange',
};

export default function ThemeTag({ theme, onDark }: Props) {
  const meta = THEMES[theme];
  return (
    <span
      className={
        'inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ' +
        (onDark ? 'bg-white/10 text-white' : 'bg-ink/[0.06] text-ink/80')
      }
    >
      <span className={`h-2 w-2 rounded-full ${DOT[meta.tag]}`} aria-hidden="true" />
      {meta.label}
    </span>
  );
}
