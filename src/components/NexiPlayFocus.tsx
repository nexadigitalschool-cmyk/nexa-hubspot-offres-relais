import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import SectionReveal from './ui/SectionReveal';

interface Props {
  onOpen: (id: string) => void;
}

const BLOCKS = [
  {
    titre: '7 mini-jeux',
    texte: "Des classiques de l'arcade version NEXA. Faciles a lancer, difficiles a lacher.",
  },
  {
    titre: 'Classement en temps reel',
    texte: 'Ton Score Nexi alimente le classement national. Ton campus compte sur toi.',
  },
  {
    titre: 'Remise a zero chaque mois',
    texte:
      'Tout le monde repart a egalite tous les mois. Le meilleur joueur repart avec des goodies NEXA.',
  },
];

// Focus Nexi'Play : parallaxe verticale legere (max 40px), desactivee si reduced-motion.
export default function NexiPlayFocus({ onOpen }: Props) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });
  const y = useTransform(scrollYProgress, [0, 1], [40, -40]);

  return (
    <section
      ref={ref}
      className="on-dark relative overflow-hidden bg-violet-dark py-20 text-white md:py-28"
    >
      <motion.div
        aria-hidden="true"
        style={reduce ? undefined : { y }}
        className="pointer-events-none absolute -right-24 top-10 h-72 w-72 rounded-full bg-violet/50 blur-[110px]"
      />
      <motion.div
        aria-hidden="true"
        style={reduce ? undefined : { y }}
        className="pointer-events-none absolute -left-20 bottom-0 h-64 w-64 rounded-full bg-cyan/20 blur-[110px]"
      />

      <div className="container-nexa relative">
        <SectionReveal>
          <span className="inline-block rounded-full bg-cyan px-4 py-1.5 text-xs font-bold uppercase tracking-wide text-ink">
            La grosse nouveaute 26-27
          </span>

          <h2 className="mt-5 max-w-3xl text-[clamp(1.9rem,5vw,3.4rem)] font-extrabold leading-tight">
            Nexi'Play, le terrain de jeu de toute la communaute
          </h2>

          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-white/85">
            Sept mini-jeux d'arcade revisites autour du code, de la data et de l'alternance, avec
            Nexi en heros. Tu joues, tu marques des points, tu fais monter ton campus au classement
            national.
          </p>
        </SectionReveal>

        <div className="mt-12 grid gap-5 md:grid-cols-3">
          {BLOCKS.map((block) => (
            <SectionReveal key={block.titre}>
              <div className="h-full rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <h3 className="text-xl font-extrabold text-cyan">{block.titre}</h3>
                <p className="mt-3 text-sm leading-relaxed text-white/80">{block.texte}</p>
              </div>
            </SectionReveal>
          ))}
        </div>

        <div className="mt-10">
          <button
            type="button"
            onClick={() => onOpen('nexi-play')}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-violet px-7 py-3 text-base font-semibold text-white shadow-violet-lg transition-all duration-200 ease-spring hover:-translate-y-0.5"
          >
            Je lance ma premiere partie <span aria-hidden="true">-&gt;</span>
          </button>
        </div>
      </div>
    </section>
  );
}
