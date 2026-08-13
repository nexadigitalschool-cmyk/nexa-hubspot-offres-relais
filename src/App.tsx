import { useCallback, useEffect } from 'react';
import { events } from './data/events';
import { useEventModalUrl } from './lib/useEventModalUrl';
import { pushDataLayer } from './lib/analytics';
import Header from './components/Header';
import Hero from './components/Hero';
import VideoSection from './components/VideoSection';
import StatsBar from './components/StatsBar';
import EventsSection from './components/EventsSection';
import NexiPlayFocus from './components/NexiPlayFocus';
import Benefits from './components/Benefits';
import Faq from './components/Faq';
import FinalCta from './components/FinalCta';
import Footer from './components/Footer';
import EventModal from './components/EventModal';

export default function App() {
  const { openId, open, close } = useEventModalUrl();
  const activeEvent = events.find((e) => e.id === openId) ?? null;

  const handleOpen = useCallback(
    (id: string) => {
      pushDataLayer('modal_open', { event_id: id });
      open(id);
    },
    [open]
  );

  // Deep-link ?event=... : trace l'ouverture automatique au chargement.
  useEffect(() => {
    if (openId) pushDataLayer('modal_open', { event_id: openId, source: 'deeplink' });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <a
        href="#evenements"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-full focus:bg-violet focus:px-5 focus:py-3 focus:text-sm focus:font-semibold focus:text-white"
      >
        Aller au contenu principal
      </a>

      <Header />

      <main>
        <Hero />
        <VideoSection />
        <StatsBar />
        <EventsSection onOpen={handleOpen} />
        <NexiPlayFocus onOpen={handleOpen} />
        <Benefits />
        <Faq />
        <FinalCta />
      </main>

      <Footer />

      <EventModal event={activeEvent} onClose={close} />
    </>
  );
}
