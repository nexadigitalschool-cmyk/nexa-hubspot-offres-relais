import { useEffect, useState } from 'react';

// Header sticky. Transparent en haut de page, fond sombre floute au scroll.
export default function Header() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <header
      className={
        'fixed inset-x-0 top-0 z-40 transition-colors duration-300 ' +
        (scrolled ? 'on-dark bg-violet-dark/85 backdrop-blur-md shadow-violet-sm' : 'bg-transparent')
      }
    >
      <div className="container-nexa flex h-16 items-center justify-between md:h-20">
        <a
          href="#top"
          className={
            'font-display text-2xl font-extrabold uppercase tracking-tight transition-colors md:text-3xl ' +
            (scrolled ? 'text-white' : 'text-violet-dark')
          }
        >
          NEXA
        </a>

        <a
          href="#evenements"
          className={
            'inline-flex min-h-[44px] items-center rounded-full px-5 py-2 text-sm font-semibold transition-all duration-200 ease-spring ' +
            (scrolled
              ? 'bg-cyan text-ink hover:-translate-y-0.5'
              : 'bg-violet text-white shadow-violet hover:-translate-y-0.5 hover:shadow-violet-lg')
          }
        >
          Voir les evenements
        </a>
      </div>
    </header>
  );
}
