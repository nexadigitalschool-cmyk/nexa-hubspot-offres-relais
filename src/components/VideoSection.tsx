import { useState } from 'react';
import SectionReveal from './ui/SectionReveal';
import { pushDataLayer } from '../lib/analytics';

// Facade video : pas d'autoplay, poster + bouton play.
// L'iframe YouTube n'est chargee qu'au clic (performance).
// >>> Remplacer VIDEO_ID par l'identifiant de la video teaser.
const VIDEO_ID = '';

export default function VideoSection() {
  const [playing, setPlaying] = useState(false);

  const handlePlay = () => {
    pushDataLayer('video_play', { video_id: VIDEO_ID || 'teaser' });
    setPlaying(true);
  };

  return (
    <section id="video" className="bg-paper py-16 md:py-24">
      <div className="container-nexa">
        <SectionReveal>
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-[clamp(1.8rem,4.5vw,3rem)] font-extrabold leading-tight text-violet-dark">
              Ton annee NEXA en 1 minute
            </h2>
            <p className="mt-4 text-lg text-ink/75">
              Tout ce qui se vit a NEXA en dehors des cours. Regarde, puis choisis.
            </p>
          </div>
        </SectionReveal>

        <SectionReveal className="mt-10">
          <div className="mx-auto max-w-4xl">
            <div className="relative aspect-video overflow-hidden rounded-2xl bg-violet-dark shadow-violet-lg">
              {playing && VIDEO_ID ? (
                <iframe
                  className="absolute inset-0 h-full w-full"
                  src={`https://www.youtube-nocookie.com/embed/${VIDEO_ID}?autoplay=1&rel=0`}
                  title="Teaser vie etudiante NEXA 2026-2027"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <button
                  type="button"
                  onClick={handlePlay}
                  className="group absolute inset-0 flex flex-col items-center justify-center gap-4"
                  aria-label="Lire le teaser video"
                >
                  {/* Poster : aplat violet sobre en attendant la vignette. */}
                  <span
                    aria-hidden="true"
                    className="grid h-20 w-20 place-items-center rounded-full bg-white/95 shadow-violet-lg transition-transform duration-200 ease-spring group-hover:scale-105"
                  >
                    <svg width="28" height="32" viewBox="0 0 28 32" fill="none">
                      <path d="M27 14.27a2 2 0 0 1 0 3.46L3 31.6A2 2 0 0 1 0 29.86V2.14A2 2 0 0 1 3 .4l24 13.87Z" fill="#6F13EE" />
                    </svg>
                  </span>
                  <span className="text-sm font-semibold uppercase tracking-wide text-white/90">
                    {VIDEO_ID ? 'Lire le teaser' : 'Video bientot disponible'}
                  </span>
                </button>
              )}
            </div>
            <p className="mt-5 text-center text-sm text-ink/60">
              Concours d'eloquence, CTF cyber, hackathons, pitchs start-up, projets d'engagement,
              soirees et Nexi'Play. Tout est juste en dessous.
            </p>
          </div>
        </SectionReveal>
      </div>
    </section>
  );
}
