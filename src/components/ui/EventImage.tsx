import { useState } from 'react';

interface Props {
  /** nom de fichier dans /public/img */
  visuel: string;
  alt: string;
  titre: string;
  className?: string;
  /** eager pour le hero uniquement, lazy partout ailleurs. */
  loading?: 'lazy' | 'eager';
}

// Affiche le visuel 16:9 de l'evenement.
// Si le fichier est absent (ex. business-game / hackathon non encore produits),
// on genere un placeholder propre : aplat violet + titre en Big Shoulders Display.
export default function EventImage({ visuel, alt, titre, className = '', loading = 'lazy' }: Props) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <div
        className={`flex items-center justify-center bg-violet-dark ${className}`}
        role="img"
        aria-label={alt}
      >
        <span className="px-6 text-center font-display text-2xl font-extrabold uppercase leading-none tracking-tight text-white md:text-4xl">
          {titre}
        </span>
      </div>
    );
  }

  return (
    <img
      src={`/img/${visuel}`}
      alt={alt}
      width={1280}
      height={720}
      loading={loading}
      decoding="async"
      className={className}
      onError={() => setFailed(true)}
    />
  );
}
