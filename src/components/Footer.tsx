export default function Footer() {
  const year = 2026;
  return (
    <footer className="bg-ink py-10 text-white/70">
      <div className="container-nexa flex flex-col items-center justify-between gap-4 text-center md:flex-row md:text-left">
        <div>
          <span className="font-display text-2xl font-extrabold uppercase tracking-tight text-white">
            NEXA
          </span>
          <p className="mt-1 text-sm">Vie etudiante {year}-{year + 1}</p>
        </div>
        <p className="max-w-md text-xs leading-relaxed text-white/50">
          Paris · Lyon · Lille · Bordeaux · Nantes · A distance. Une question ? Rapproche-toi de ton
          referent vie etudiante sur ton campus.
        </p>
      </div>
    </footer>
  );
}
