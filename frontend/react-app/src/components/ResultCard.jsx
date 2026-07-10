import useCountUp from "../useCountUp";
import { VILLE_PRIX_M2_REFERENCE } from "../api";

const formatFcfa = (n) =>
  new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(
    Math.round(n)
  );

export default function ResultCard({ result, ville, surface, status, errorMessage }) {
  const animatedPrice = useCountUp(result?.prix_loyer_mensuel_estime ?? null);

  const referencePrice =
    ville && surface ? VILLE_PRIX_M2_REFERENCE[ville] * surface : null;
  const ratio =
    result && referencePrice
      ? result.prix_loyer_mensuel_estime / referencePrice
      : null;
  const barWidth = ratio ? Math.min(Math.max(ratio * 50, 8), 100) : 0;

  return (
    <div
      className="sticky top-6 rounded-2xl border-2 border-dashed border-encre/25 bg-white/70 p-6 backdrop-blur-sm"
      aria-live="polite"
    >
      <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-brume">
        Fiche d&rsquo;estimation
      </p>

      {status === "idle" && (
        <p className="mt-4 text-[15px] text-brume">
          Remplissez le formulaire pour obtenir une estimation du loyer
          mensuel.
        </p>
      )}

      {status === "error" && (
        <p className="mt-4 text-[15px] text-argile-dark">{errorMessage}</p>
      )}

      {(status === "loading" || status === "success") && (
        <>
          <div className="mt-3 flex items-baseline gap-2 font-mono">
            <span
              className={`text-4xl font-medium text-encre transition-opacity sm:text-5xl ${
                status === "loading" ? "opacity-40" : "opacity-100"
              }`}
            >
              {formatFcfa(animatedPrice)}
            </span>
            <span className="text-base text-brume">FCFA / mois</span>
          </div>

          {referencePrice && result && (
            <div className="mt-5">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-brume-light">
                <div
                  className="h-full rounded-full bg-palmier transition-all duration-700"
                  style={{ width: `${barWidth}%` }}
                />
              </div>
              <p className="mt-2 text-[13px] text-brume">
                {ratio > 1.05
                  ? `Au-dessus du prix de référence pour ${ville}`
                  : ratio < 0.95
                  ? `En dessous du prix de référence pour ${ville}`
                  : `Proche du prix de référence pour ${ville}`}
              </p>
            </div>
          )}

          {result && (
            <p className="mt-5 font-mono text-[12px] text-brume">
              modèle : {result.model_version}
            </p>
          )}
        </>
      )}
    </div>
  );
}
