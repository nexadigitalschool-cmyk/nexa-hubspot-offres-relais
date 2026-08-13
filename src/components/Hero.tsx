import { motion, useReducedMotion } from 'framer-motion';

// Hero : surtitre, H1 apparaissant mot par mot en blur-in, sous-titre, 2 CTA, micro-mention.
const H1_WORDS = ['Il', 'se', 'passe', 'toujours', 'quelque', 'chose', 'a', 'NEXA'];

export default function Hero() {
  const reduce = useReducedMotion();

  return (
    <section
      id="top"
      className="on-dark relative overflow-hidden bg-violet-dark pb-20 pt-28 text-white md:pb-28 md:pt-36"
    >
      {/* Halo violet discret, sans degrade criard. */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-violet/40 blur-[120px]"
      />

      <div className="container-nexa relative">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-cyan md:text-base">
          Vie etudiante NEXA 2026-2027
        </p>

        <h1 className="max-w-4xl text-[clamp(2.4rem,7vw,5rem)] font-extrabold uppercase leading-[0.95] tracking-tight">
          {H1_WORDS.map((word, i) => (
            <motion.span
              key={`${word}-${i}`}
              className="mr-[0.25em] inline-block"
              initial={reduce ? { opacity: 0 } : { opacity: 0, filter: 'blur(12px)', y: 8 }}
              animate={reduce ? { opacity: 1 } : { opacity: 1, filter: 'blur(0px)', y: 0 }}
              transition={{ duration: 0.5, delay: reduce ? 0 : 0.15 + i * 0.08, ease: [0.22, 1, 0.36, 1] }}
            >
              {word}
            </motion.span>
          ))}
        </h1>

        <p className="mt-6 max-w-2xl text-[clamp(1rem,2.2vw,1.25rem)] font-normal leading-relaxed text-white/85">
          Eloquence, competitions cyber, entrepreneuriat, hackathons, engagement, soirees et gaming.
          Une annee entiere de temps forts sur tous les campus. A toi de choisir ceux qui te
          ressemblent.
        </p>

        <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:items-center">
          <a
            href="#evenements"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-violet px-7 py-3 text-base font-semibold text-white shadow-violet transition-all duration-200 ease-spring hover:-translate-y-0.5 hover:shadow-violet-lg"
          >
            Voir tous les evenements <span aria-hidden="true">-&gt;</span>
          </a>
          <a
            href="#video"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full border-2 border-white/30 px-7 py-3 text-base font-semibold text-white transition-all duration-200 ease-spring hover:border-cyan hover:text-cyan"
          >
            Regarder le teaser <span aria-hidden="true">-&gt;</span>
          </a>
        </div>

        <p className="mt-6 text-sm text-white/55">
          Places limitees sur la plupart des evenements. Pre-inscris-toi tot.
        </p>
      </div>
    </section>
  );
}
