import { useCountUp } from '../hooks/useCountUp';
import SectionReveal from './ui/SectionReveal';

interface Stat {
  value: number;
  suffix?: string;
  label: string;
}

const STATS: Stat[] = [
  { value: 6, label: 'campus mobilises' },
  { value: 11, label: 'temps forts sur l\'annee' },
  { value: 2, label: 'finales nationales, Lyon et Paris' },
  { value: 100, suffix: ' %', label: 'des frais de deplacement pris en charge pour les finales' },
];

function StatItem({ value, suffix, label }: Stat) {
  const { ref, value: current } = useCountUp(value);
  return (
    <div className="text-center">
      <div className="font-display text-[clamp(2.5rem,6vw,4rem)] font-extrabold leading-none text-cyan">
        <span ref={ref}>{current}</span>
        {suffix}
      </div>
      <p className="mx-auto mt-2 max-w-[16ch] text-sm text-white/75 md:text-base">{label}</p>
    </div>
  );
}

// Bandeau chiffres, count-up a l'entree dans le viewport.
export default function StatsBar() {
  return (
    <section className="on-dark bg-violet py-14 text-white md:py-20">
      <div className="container-nexa">
        <SectionReveal>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-10 md:grid-cols-4">
            {STATS.map((stat) => (
              <StatItem key={stat.label} {...stat} />
            ))}
          </dl>
        </SectionReveal>
      </div>
    </section>
  );
}
