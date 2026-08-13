import { useCallback, useEffect, useState } from 'react';
import { events } from '../data/events';

// Gere le parametre ?event=<id> :
//   - au chargement, si present et valide, ouvre la modale correspondante ;
//   - a l'ouverture/fermeture, met a jour l'URL (partage de lien direct).

function readEventFromUrl(): string | null {
  if (typeof window === 'undefined') return null;
  const id = new URLSearchParams(window.location.search).get('event');
  if (id && events.some((e) => e.id === id)) return id;
  return null;
}

function writeEventToUrl(id: string | null): void {
  if (typeof window === 'undefined') return;
  const params = new URLSearchParams(window.location.search);
  if (id) {
    params.set('event', id);
  } else {
    params.delete('event');
  }
  const query = params.toString();
  const newUrl = `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`;
  window.history.replaceState(null, '', newUrl);
}

export function useEventModalUrl() {
  const [openId, setOpenId] = useState<string | null>(() => readEventFromUrl());

  useEffect(() => {
    writeEventToUrl(openId);
  }, [openId]);

  useEffect(() => {
    const onPop = () => setOpenId(readEventFromUrl());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const open = useCallback((id: string) => setOpenId(id), []);
  const close = useCallback(() => setOpenId(null), []);

  return { openId, open, close };
}
