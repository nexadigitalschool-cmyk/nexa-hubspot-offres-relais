import Chip from './ui/Chip';
import { THEMES, THEME_ORDER, CAMPUS, type EventTheme } from '../data/events';
import type { FiltersState } from '../lib/useUrlFilters';

interface Props {
  filters: FiltersState;
  count: number;
  onToggleTheme: (theme: EventTheme) => void;
  onClearThemes: () => void;
  onSetCampus: (campus: string | null) => void;
}

// Barre de filtres sticky sous le header.
// Chips thematiques multi-selection + select campus + compteur dynamique.
export default function FilterBar({
  filters,
  count,
  onToggleTheme,
  onClearThemes,
  onSetCampus,
}: Props) {
  const allActive = filters.themes.length === 0;

  return (
    <div className="sticky top-16 z-30 border-b border-ink/10 bg-paper/90 backdrop-blur-md md:top-20">
      <div className="container-nexa py-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Chips thematiques : scroll horizontal snap sur mobile, jamais de retour ligne. */}
          <div
            className="filter-fade no-scrollbar -mx-6 flex snap-x gap-2 overflow-x-auto px-6 md:mx-0 md:flex-wrap md:overflow-visible md:px-0"
            role="group"
            aria-label="Filtrer par thematique"
          >
            <Chip active={allActive} onClick={onClearThemes} className="snap-start">
              Tout
            </Chip>
            {THEME_ORDER.map((theme) => (
              <Chip
                key={theme}
                active={filters.themes.includes(theme)}
                onClick={() => onToggleTheme(theme)}
                className="snap-start"
              >
                {THEMES[theme].label}
              </Chip>
            ))}
          </div>

          {/* Filtre campus secondaire + compteur. */}
          <div className="flex items-center justify-between gap-4 md:justify-end">
            <label className="flex items-center gap-2 text-sm text-ink/70">
              <span className="hidden md:inline">Campus</span>
              <select
                value={filters.campus ?? ''}
                onChange={(e) => onSetCampus(e.target.value || null)}
                className="min-h-[44px] rounded-full border border-ink/15 bg-white px-4 py-2 text-sm font-semibold text-ink/80 focus-visible:outline-offset-2"
                aria-label="Filtrer par campus"
              >
                <option value="">Tous les campus</option>
                {CAMPUS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>

            <span
              className="whitespace-nowrap text-sm font-semibold text-violet"
              aria-live="polite"
            >
              {count} evenement{count > 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
