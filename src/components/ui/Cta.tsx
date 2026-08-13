import type { ButtonHTMLAttributes } from 'react';
import type { CtaState } from '../../lib/ctaState';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  state: CtaState;
  fullWidth?: boolean;
}

// Rend le bon bouton selon l'etat CTA calcule (solid / outline / disabled).
// Un bouton desactive reste focusable mais porte aria-disabled + title.
export default function Cta({ state, fullWidth, className = '', onClick, ...rest }: Props) {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-full font-body font-semibold ' +
    'px-6 py-3 text-sm md:text-base min-h-[44px] transition-all duration-200 ease-spring ' +
    'focus-visible:outline-offset-2';

  const width = fullWidth ? 'w-full' : '';

  const variants: Record<CtaState['variant'], string> = {
    solid:
      'bg-violet text-white shadow-violet hover:-translate-y-0.5 hover:shadow-violet-lg active:translate-y-0',
    outline:
      'border-2 border-cyan text-violet-dark bg-white/70 hover:bg-cyan/15 hover:-translate-y-0.5',
    disabled: 'bg-ink/10 text-ink/45 cursor-not-allowed',
  };

  const handleClick: Props['onClick'] = (e) => {
    if (state.disabled || !state.actionable) {
      e.preventDefault();
      return;
    }
    onClick?.(e);
  };

  return (
    <button
      type="button"
      className={`${base} ${variants[state.variant]} ${width} ${className}`}
      onClick={handleClick}
      aria-disabled={state.disabled || undefined}
      title={state.title}
      {...rest}
    >
      {state.label}
    </button>
  );
}
