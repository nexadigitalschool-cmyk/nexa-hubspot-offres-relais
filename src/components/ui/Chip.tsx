import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  active?: boolean;
  children: ReactNode;
}

// Chip de filtre : pilule multi-selection.
export default function Chip({ active, children, className = '', ...rest }: Props) {
  const base =
    'inline-flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm font-semibold ' +
    'min-h-[44px] whitespace-nowrap transition-all duration-200 ease-spring ' +
    'focus-visible:outline-offset-2';

  const state = active
    ? 'bg-violet text-white border-violet shadow-violet-sm'
    : 'bg-white text-ink/70 border-ink/15 hover:border-violet/50 hover:text-violet';

  return (
    <button
      type="button"
      aria-pressed={active}
      className={`${base} ${state} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
