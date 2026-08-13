import SectionReveal from './ui/SectionReveal';

export default function FinalCta() {
  return (
    <section className="on-dark relative overflow-hidden bg-violet py-20 text-white md:py-28">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-violet-dark/50 blur-[120px]"
      />
      <div className="container-nexa relative text-center">
        <SectionReveal>
          <h2 className="mx-auto max-w-3xl text-[clamp(1.9rem,5vw,3.4rem)] font-extrabold leading-tight">
            Les places sont limitees
          </h2>
          <p className="mx-auto mt-5 max-w-2xl text-lg leading-relaxed text-white/85">
            Pre-inscris-toi des maintenant sur les evenements qui t'interessent. Les premiers
            inscrits sont les premiers servis, et certaines selections se ferment vite.
          </p>
          <a
            href="#evenements"
            className="mt-9 inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-white px-8 py-3 text-base font-semibold text-violet shadow-violet-lg transition-all duration-200 ease-spring hover:-translate-y-0.5"
          >
            Je choisis mes evenements <span aria-hidden="true">-&gt;</span>
          </a>
          <p className="mt-6 text-sm text-white/60">
            Une question ? Contacte ton referent vie etudiante sur ton campus.
          </p>
        </SectionReveal>
      </div>
    </section>
  );
}
