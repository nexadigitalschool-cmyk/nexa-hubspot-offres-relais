import SectionReveal from './ui/SectionReveal';

const BENEFITS = [
  {
    titre: 'Ca se raconte en entretien',
    texte:
      "Un concours d'eloquence, un hackathon boucle en 24h ou un CTF national, ca marque bien plus qu'une ligne de competence sur ton CV. Tes recruteurs et ton tuteur d'alternance s'en souviennent.",
  },
  {
    titre: 'Tu es coache par des pros',
    texte:
      "NEX LEADER et NEX LAB, ce ne sont pas des ateliers improvises. Tu beneficies d'un accompagnement individuel par des professionnels, en visio, en dehors de tes heures de formation.",
  },
  {
    titre: 'Tu sors de ta promo',
    texte:
      'Demi-finales sur ton campus, finales nationales a Lyon et a Paris. Tu rencontres les etudiants des 6 campus et tu decouvres d\'autres filieres que la tienne.',
  },
  {
    titre: "L'ecole prend en charge tes deplacements",
    texte:
      'Si tu vas en finale nationale, tes frais sont couverts. Aucune raison de se dire que c\'est trop loin.',
  },
  {
    titre: 'Certaines actions comptent dans ton evaluation',
    texte:
      "Le projet d'engagement NEX IN est integre a ton bulletin. Tu construis quelque chose d'utile et ca se voit dans tes resultats.",
  },
  {
    titre: 'Et tu passes une bonne annee',
    texte:
      "Le Cluedo geant, la Gaming Night, Nexi'Play. C'est aussi la que se creent les meilleurs souvenirs de ton alternance.",
  },
];

export default function Benefits() {
  return (
    <section className="bg-paper py-16 md:py-24">
      <div className="container-nexa">
        <SectionReveal>
          <div className="max-w-3xl">
            <h2 className="text-[clamp(1.8rem,4.5vw,3rem)] font-extrabold leading-tight text-violet-dark">
              Pourquoi ca vaut le coup
            </h2>
            <p className="mt-4 text-lg text-ink/75">
              Ce n'est pas juste du bonus. Ce que tu vis ici te sert directement.
            </p>
          </div>
        </SectionReveal>

        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {BENEFITS.map((benefit, i) => (
            <SectionReveal key={benefit.titre}>
              <div className="h-full rounded-2xl bg-white p-6 shadow-violet-sm">
                <span className="font-display text-3xl font-extrabold text-cyan">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="mt-3 text-lg font-extrabold text-ink">{benefit.titre}</h3>
                <p className="mt-2 text-sm leading-relaxed text-ink/70">{benefit.texte}</p>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  );
}
