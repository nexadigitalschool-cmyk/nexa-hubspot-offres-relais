import { useMemo } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { events } from '../data/events';
import { useUrlFilters } from '../lib/useUrlFilters';
import { staggerContainer, VIEWPORT_ONCE } from '../lib/motion';
import FilterBar from './FilterBar';
import EventCard from './EventCard';
import SectionReveal from './ui/SectionReveal';

interface Props {
  onOpen: (id: string) => void;
}

export default function EventsSection({ onOpen }: Props) {
  const reduce = useReducedMotion();
  const { filters, toggleTheme, clearThemes, setCampus, reset } = useUrlFilters();

  const filtered = useMemo(() => {
    return events.filter((event) => {
      const themeOk = filters.themes.length === 0 || filters.themes.includes(event.theme);
      const campusOk =
        !filters.campus ||
        event.campus.includes('tous') ||
        event.campus.includes(filters.campus);
      return themeOk && campusOk;
    });
  }, [filters]);

  return (
    <section id="evenements" className="bg-paper pb-20 pt-14 md:pb-28">
      <div className="container-nexa">
        <SectionReveal>
          <div className="max-w-3xl">
            <h2 className="text-[clamp(1.8rem,4.5vw,3rem)] font-extrabold leading-tight text-violet-dark">
              Choisis tes temps forts
            </h2>
            <p className="mt-4 text-lg text-ink/75">
              Filtre par thematique et repere ce qui te correspond. Certaines inscriptions sont deja
              ouvertes, d'autres arrivent tres vite. Cette page est mise a jour toute l'annee,
              garde-la en favori.
            </p>
          </div>
        </SectionReveal>
      </div>

      <div className="mt-8">
        <FilterBar
          filters={filters}
          count={filtered.length}
          onToggleTheme={toggleTheme}
          onClearThemes={clearThemes}
          onSetCampus={setCampus}
        />
      </div>

      <div className="container-nexa mt-10">
        {filtered.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-ink/20 bg-white/60 p-10 text-center">
            <p className="text-lg text-ink/70">
              Aucun evenement sur cette thematique pour le moment.
            </p>
            <button
              type="button"
              onClick={reset}
              className="mt-4 inline-flex min-h-[44px] items-center rounded-full bg-violet px-6 py-3 text-sm font-semibold text-white shadow-violet transition-all duration-200 ease-spring hover:-translate-y-0.5"
            >
              Voir tout
            </button>
          </div>
        ) : (
          <motion.div
            className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
            variants={reduce ? undefined : staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={VIEWPORT_ONCE}
          >
            <AnimatePresence mode="popLayout">
              {filtered.map((event) => (
                <EventCard key={event.id} event={event} onOpen={onOpen} />
              ))}
            </AnimatePresence>
          </motion.div>
        )}

        <p className="mt-10 text-center text-sm text-ink/60">
          D'autres evenements arrivent tout au long de l'annee. Cette page est mise a jour en
          continu.
        </p>
      </div>
    </section>
  );
}
