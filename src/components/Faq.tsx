import { useState } from 'react';
import SectionReveal from './ui/SectionReveal';

const FAQ = [
  {
    q: 'Je peux participer a plusieurs evenements ?',
    a: 'Oui, autant que tu veux. Les seules limites sont ton emploi du temps et le nombre de places.',
  },
  {
    q: 'Est-ce que ca empiete sur mes cours ou mon alternance ?',
    a: "Non. Les coachings NEX LEADER et NEX LAB se deroulent en visio, hors heures de formation. Les autres evenements sont cales sur des creneaux compatibles avec ton rythme d'alternance.",
  },
  {
    q: 'Je suis en distanciel, je peux participer ?',
    a: 'Oui pour tout ce qui est en ligne : Nexi\'Play, les CTF en ligne, les coachings visio. Pour les temps forts en presentiel, rapproche-toi de ton campus de rattachement.',
  },
  {
    q: 'Est-ce que ca coute quelque chose ?',
    a: 'Non. La participation est gratuite et les frais de deplacement pour les finales nationales sont pris en charge par l\'ecole.',
  },
  {
    q: "Il n'y a pas encore de lien d'inscription sur l'evenement qui m'interesse.",
    a: "C'est normal, les inscriptions ouvrent au fil de l'annee. Le bouton passe automatiquement en « Je m'inscris » des que c'est ouvert. Reviens sur cette page ou surveille ta newsletter etudiante.",
  },
];

function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-2xl bg-white shadow-violet-sm">
      <h3>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left text-base font-semibold text-ink"
        >
          {q}
          <span
            aria-hidden="true"
            className={
              'grid h-7 w-7 shrink-0 place-items-center rounded-full bg-violet/10 text-lg leading-none text-violet transition-transform duration-200 ' +
              (open ? 'rotate-45' : '')
            }
          >
            +
          </span>
        </button>
      </h3>
      <div
        className={
          'grid overflow-hidden transition-all duration-300 ease-spring ' +
          (open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0')
        }
      >
        <div className="min-h-0">
          <p className="px-6 pb-5 text-sm leading-relaxed text-ink/75">{a}</p>
        </div>
      </div>
    </div>
  );
}

export default function Faq() {
  return (
    <section className="bg-paper py-16 md:py-24">
      <div className="container-nexa">
        <SectionReveal>
          <h2 className="text-[clamp(1.8rem,4.5vw,3rem)] font-extrabold leading-tight text-violet-dark">
            Les questions que tu te poses
          </h2>
        </SectionReveal>

        <div className="mx-auto mt-10 flex max-w-3xl flex-col gap-3">
          {FAQ.map((item) => (
            <SectionReveal key={item.q}>
              <FaqItem {...item} />
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
