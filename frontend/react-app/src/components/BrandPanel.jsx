import Skyline from "./Skyline";

export default function BrandPanel() {
  return (
    <aside className="relative flex flex-col justify-between overflow-hidden bg-encre text-sable px-8 py-10 md:min-h-screen md:w-[38%] md:px-12 md:py-14">
      <div>
        <div className="flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">
            <rect width="32" height="32" rx="6" fill="#C1592B" />
            <path d="M4 22 L11 12 L16 18 L21 9 L28 22 Z" fill="#FBF6EF" />
          </svg>
          <span className="font-display text-lg tracking-wide">Sénégal Immo</span>
        </div>

        <h1 className="font-display mt-10 text-4xl leading-[1.1] font-semibold md:mt-16 md:text-5xl">
          Estimez un loyer
          <br />
          en <span className="text-argile">quelques secondes.</span>
        </h1>
        <p className="mt-5 max-w-sm text-[15px] leading-relaxed text-brume-light">
          Renseignez les caractéristiques du bien — ville, surface,
          équipements — et obtenez une estimation du loyer mensuel calculée
          par notre modèle, entraîné sur les données du marché locatif
          sénégalais.
        </p>
      </div>

      <div className="mt-16 md:mt-0">
        <Skyline />
      </div>
    </aside>
  );
}
