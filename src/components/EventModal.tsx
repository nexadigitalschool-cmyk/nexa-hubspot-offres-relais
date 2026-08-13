import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion, type PanInfo } from 'framer-motion';
import type { NexaEvent } from '../data/events';
import { pushDataLayer } from '../lib/analytics';
import EventImage from './ui/EventImage';
import ThemeTag from './ui/ThemeTag';

interface Props {
  event: NexaEvent | null;
  onClose: () => void;
}

const FOCUSABLE =
  'a[href], button:not([disabled]), textarea, input, select, iframe, [tabindex]:not([tabindex="-1"])';

export default function EventModal({ event, onClose }: Props) {
  const reduce = useReducedMotion();
  const panelRef = useRef<HTMLDivElement | null>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  // Verrou du scroll body sans saut de mise en page + focus management.
  useEffect(() => {
    if (!event) return;

    triggerRef.current = document.activeElement as HTMLElement | null;

    const scrollbar = window.innerWidth - document.documentElement.clientWidth;
    const prevOverflow = document.body.style.overflow;
    const prevPad = document.body.style.paddingRight;
    document.body.style.overflow = 'hidden';
    if (scrollbar > 0) document.body.style.paddingRight = `${scrollbar}px`;

    // Focus initial sur le panneau.
    const focusTimer = window.setTimeout(() => {
      panelRef.current?.focus();
    }, 0);

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }
      if (e.key === 'Tab' && panelRef.current) {
        const nodes = panelRef.current.querySelectorAll<HTMLElement>(FOCUSABLE);
        if (nodes.length === 0) return;
        const first = nodes[0];
        const last = nodes[nodes.length - 1];
        const activeEl = document.activeElement;
        if (e.shiftKey && (activeEl === first || activeEl === panelRef.current)) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && activeEl === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener('keydown', onKeyDown);

    return () => {
      window.clearTimeout(focusTimer);
      document.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = prevOverflow;
      document.body.style.paddingRight = prevPad;
      // Rend le focus au declencheur.
      triggerRef.current?.focus?.();
    };
  }, [event, onClose]);

  const handleDragEnd = (_: unknown, info: PanInfo) => {
    if (info.offset.y > 120 || info.velocity.y > 600) onClose();
  };

  return (
    <AnimatePresence>
      {event && (
        <motion.div
          className="on-dark fixed inset-0 z-50 flex items-end justify-center sm:items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Overlay : clic pour fermer. */}
          <div
            className="absolute inset-0 bg-ink/70 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />

          <motion.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="event-modal-title"
            tabIndex={-1}
            className="relative flex max-h-[92vh] w-full max-w-2xl flex-col overflow-hidden rounded-t-2xl bg-white shadow-violet-lg outline-none sm:rounded-2xl"
            initial={
              reduce
                ? { opacity: 0 }
                : { opacity: 0, y: '100%', scale: 1 }
            }
            animate={
              reduce
                ? { opacity: 1 }
                : { opacity: 1, y: 0, scale: 1 }
            }
            exit={reduce ? { opacity: 0 } : { opacity: 0, y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            drag={reduce ? false : 'y'}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.4 }}
            onDragEnd={handleDragEnd}
          >
            {/* Poignee mobile (drag-to-dismiss). */}
            <div className="flex justify-center pt-2 sm:hidden">
              <span className="h-1.5 w-12 rounded-full bg-ink/20" aria-hidden="true" />
            </div>

            <div className="overflow-y-auto">
              <ModalContent event={event} onClose={onClose} />
            </div>

            <button
              type="button"
              onClick={onClose}
              aria-label="Fermer"
              className="absolute right-3 top-3 z-10 grid h-10 w-10 place-items-center rounded-full bg-ink/60 text-white transition-colors hover:bg-ink/80"
            >
              <span aria-hidden="true" className="text-xl leading-none">
                &times;
              </span>
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function ModalContent({ event, onClose }: { event: NexaEvent; onClose: () => void }) {
  const campusLabel = event.campus.includes('tous')
    ? 'Tous les campus'
    : event.campus.join(', ');

  return (
    <>
      <div className="relative aspect-video w-full overflow-hidden bg-violet-dark">
        <EventImage
          visuel={event.visuel}
          alt={event.alt}
          titre={event.titre}
          className="h-full w-full object-cover"
        />
      </div>

      <div className="p-5 md:p-7">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <ThemeTag theme={event.theme} />
          {event.badge && (
            <span className="rounded-full bg-orange/15 px-3 py-1 text-xs font-bold uppercase tracking-wide text-orange">
              {event.badge}
            </span>
          )}
        </div>

        <h2
          id="event-modal-title"
          className="text-[clamp(1.6rem,4vw,2.4rem)] font-extrabold leading-tight text-violet-dark"
        >
          {event.titre}
        </h2>
        <p className="mt-1 text-base font-semibold text-ink">{event.accroche}</p>

        <p className="mt-4 text-sm leading-relaxed text-ink/75 md:text-base">
          {event.descriptionModale}
        </p>

        {event.infos.length > 0 && (
          <ul className="mt-5 flex flex-wrap gap-x-4 gap-y-2 text-sm font-medium text-violet-dark/85">
            {event.infos.map((info) => (
              <li key={info} className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-violet" aria-hidden="true" />
                {info}
              </li>
            ))}
          </ul>
        )}

        <p className="mt-4 text-sm text-ink/60">
          <span className="font-semibold text-ink/80">Campus concernes :</span> {campusLabel}
        </p>

        <div className="mt-6 border-t border-ink/10 pt-6">
          <FormZone event={event} onClose={onClose} />
        </div>
      </div>
    </>
  );
}

// Zone formulaire, 3 cas (brief section 9).
function FormZone({ event, onClose }: { event: NexaEvent; onClose: () => void }) {
  const [iframeLoaded, setIframeLoaded] = useState(false);

  if (event.statut === 'ferme') {
    return (
      <p className="rounded-xl bg-ink/5 p-4 text-sm text-ink/70">
        Les inscriptions pour cet evenement sont closes.
      </p>
    );
  }

  // Cas 1 : formulaire integre en iframe.
  if (event.formEmbedUrl) {
    return (
      <div className="relative">
        {!iframeLoaded && (
          <div className="absolute inset-0 animate-pulse rounded-xl bg-ink/5" aria-hidden="true" />
        )}
        <iframe
          src={event.formEmbedUrl}
          title={`Formulaire d'inscription - ${event.titre}`}
          loading="lazy"
          onLoad={() => setIframeLoaded(true)}
          className="min-h-[600px] w-full rounded-xl border border-ink/10"
        />
      </div>
    );
  }

  // Cas 2 : lien externe.
  if (event.formLinkUrl) {
    return (
      <a
        href={event.formLinkUrl}
        target="_blank"
        rel="noopener noreferrer"
        onClick={() =>
          pushDataLayer('outbound_click', { event_id: event.id, url: event.formLinkUrl })
        }
        className="inline-flex min-h-[44px] w-full items-center justify-center gap-2 rounded-full bg-violet px-6 py-3 text-base font-semibold text-white shadow-violet transition-all duration-200 ease-spring hover:-translate-y-0.5 hover:shadow-violet-lg"
      >
        {event.ctaLabel ?? (event.statut === 'selection' ? 'Je candidate' : "Je m'inscris")}
        <span aria-hidden="true">-&gt;</span>
      </a>
    );
  }

  // Cas 3 : aucune URL renseignee.
  return (
    <div className="rounded-xl bg-violet/5 p-4">
      <p className="text-sm text-ink/75">
        Les inscriptions ne sont pas encore ouvertes. Reviens sur cette page ou surveille ta
        newsletter etudiante.
      </p>
      <button
        type="button"
        onClick={onClose}
        className="mt-3 text-sm font-semibold text-violet underline underline-offset-2 hover:text-violet-dark"
      >
        Fermer
      </button>
    </div>
  );
}
