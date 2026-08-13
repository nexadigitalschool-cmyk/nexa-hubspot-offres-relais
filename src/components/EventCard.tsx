import { motion, useReducedMotion } from 'framer-motion';
import type { NexaEvent } from '../data/events';
import { getCtaState } from '../lib/ctaState';
import { pushDataLayer } from '../lib/analytics';
import { cardItem, cardItemReduced } from '../lib/motion';
import EventImage from './ui/EventImage';
import ThemeTag from './ui/ThemeTag';
import Cta from './ui/Cta';

interface Props {
  event: NexaEvent;
  onOpen: (id: string) => void;
}

// Card evenement. Le titre est deja dans le visuel : le <h3> HTML est present
// pour l'accessibilite/SEO mais masque visuellement.
export default function EventCard({ event, onOpen }: Props) {
  const reduce = useReducedMotion();
  const cta = getCtaState(event);

  const handleCta = () => {
    pushDataLayer('cta_card_click', { event_id: event.id, statut: event.statut });
    onOpen(event.id);
  };

  return (
    <motion.article
      layout
      variants={reduce ? cardItemReduced : cardItem}
      className="group flex h-full flex-col overflow-hidden rounded-2xl bg-white shadow-violet-sm transition-all duration-300 ease-spring hover:-translate-y-1.5 hover:shadow-violet-lg motion-reduce:hover:translate-y-0"
    >
      {/* Visuel 16:9, zoom au hover (desactive au tactile via group + overflow hidden). */}
      <div className="relative aspect-video overflow-hidden bg-violet-dark">
        <EventImage
          visuel={event.visuel}
          alt={event.alt}
          titre={event.titre}
          className="h-full w-full object-cover transition-transform duration-500 ease-spring group-hover:scale-[1.04] motion-reduce:group-hover:scale-100"
        />
        {event.badge && (
          <span className="absolute left-3 top-3 rounded-full bg-orange px-3 py-1 text-xs font-bold uppercase tracking-wide text-white shadow-violet-sm">
            {event.badge}
          </span>
        )}
        {event.dateAffichee && (
          <span className="absolute right-3 top-3 rounded-full bg-ink/70 px-3 py-1 text-xs font-semibold text-white backdrop-blur-sm">
            {event.dateAffichee}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col p-5">
        <h3 className="sr-only-title">{event.titre}</h3>

        <div className="mb-3">
          <ThemeTag theme={event.theme} />
        </div>

        <p className="text-base font-semibold text-ink">{event.accroche}</p>
        <p className="mt-2 text-sm leading-relaxed text-ink/70">{event.descriptionCard}</p>

        {event.infos.length > 0 && (
          <ul className="mt-4 flex flex-wrap gap-x-3 gap-y-1 text-xs font-medium text-violet-dark/80">
            {event.infos.map((info) => (
              <li key={info} className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-violet" aria-hidden="true" />
                {info}
              </li>
            ))}
          </ul>
        )}

        {/* CTA colle en bas pour une hauteur de card uniforme. */}
        <div className="mt-auto pt-5">
          <Cta state={cta} fullWidth onClick={handleCta} />
        </div>
      </div>
    </motion.article>
  );
}
