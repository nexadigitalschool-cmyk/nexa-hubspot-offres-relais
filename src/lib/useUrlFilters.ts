import { useCallback, useEffect, useState } from 'react';
import type { EventTheme } from '../data/events';

// Etat des filtres synchronise avec l'URL, sans rechargement.
//   ?theme=competitions,soirees   -> themes selectionnes
//   ?campus=Lyon                  -> campus selectionne (secondaire)
// Une selection vide = "Tout" (aucun filtre applique).

export interface FiltersState {
  themes: EventTheme[];
  campus: string | null;
}

const VALID_THEMES: EventTheme[] = [
  'competitions',
  'leadership',
  'entrepreneuriat',
  'engagement',
  'challenges',
  'soirees',
];

function readFromUrl(): FiltersState {
  if (typeof window === 'undefined') return { themes: [], campus: null };
  const params = new URLSearchParams(window.location.search);

  const rawThemes = params.get('theme');
  const themes = rawThemes
    ? (rawThemes.split(',').filter((t): t is EventTheme => VALID_THEMES.includes(t as EventTheme)))
    : [];

  const campus = params.get('campus');

  return { themes, campus: campus || null };
}

function writeToUrl(state: FiltersState): void {
  if (typeof window === 'undefined') return;
  const params = new URLSearchParams(window.location.search);

  if (state.themes.length > 0) {
    params.set('theme', state.themes.join(','));
  } else {
    params.delete('theme');
  }

  if (state.campus) {
    params.set('campus', state.campus);
  } else {
    params.delete('campus');
  }

  const query = params.toString();
  const newUrl = `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`;
  window.history.replaceState(null, '', newUrl);
}

export function useUrlFilters() {
  const [filters, setFilters] = useState<FiltersState>(() => readFromUrl());

  // Reflet dans l'URL a chaque changement.
  useEffect(() => {
    writeToUrl(filters);
  }, [filters]);

  // Re-lecture si l'utilisateur navigue (bouton precedent/suivant).
  useEffect(() => {
    const onPop = () => setFilters(readFromUrl());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const toggleTheme = useCallback((theme: EventTheme) => {
    setFilters((prev) => {
      const active = prev.themes.includes(theme);
      return {
        ...prev,
        themes: active ? prev.themes.filter((t) => t !== theme) : [...prev.themes, theme],
      };
    });
  }, []);

  const clearThemes = useCallback(() => {
    setFilters((prev) => ({ ...prev, themes: [] }));
  }, []);

  const setCampus = useCallback((campus: string | null) => {
    setFilters((prev) => ({ ...prev, campus }));
  }, []);

  const reset = useCallback(() => {
    setFilters({ themes: [], campus: null });
  }, []);

  return { filters, toggleTheme, clearThemes, setCampus, reset };
}
