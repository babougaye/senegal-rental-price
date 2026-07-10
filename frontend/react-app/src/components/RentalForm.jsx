import { EQUIPEMENTS, TYPES_BIEN, VILLES } from "../api";

const fieldLabel =
  "block text-[13px] font-medium tracking-wide text-brume uppercase mb-1.5";
const inputBase =
  "w-full rounded-lg border border-brume-light bg-white px-3.5 py-2.5 text-[15px] text-encre outline-none transition-colors focus:border-argile focus:ring-2 focus:ring-argile/20";

export default function RentalForm({ values, errors, onChange, onSubmit, isSubmitting }) {
  const handleField = (field) => (e) => {
    const raw = e.target.value;
    const value =
      e.target.type === "number" ? (raw === "" ? "" : Number(raw)) : raw;
    onChange(field, value);
  };

  const toggleEquipement = (equip) => {
    const current = values.equipements;
    const next = current.includes(equip)
      ? current.filter((e) => e !== equip)
      : [...current, equip];
    onChange("equipements", next);
  };

  return (
    <form
      onSubmit={onSubmit}
      className="space-y-6"
      aria-describedby={errors.length ? "form-errors" : undefined}
    >
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div>
          <label className={fieldLabel} htmlFor="ville">Ville</label>
          <select
            id="ville"
            className={inputBase}
            value={values.ville}
            onChange={handleField("ville")}
          >
            {VILLES.map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>

        <div>
          <label className={fieldLabel} htmlFor="quartier">
            Quartier <span className="normal-case text-brume/70">(optionnel)</span>
          </label>
          <input
            id="quartier"
            type="text"
            placeholder="ex. Almadies"
            className={inputBase}
            value={values.quartier}
            onChange={handleField("quartier")}
          />
        </div>

        <div>
          <label className={fieldLabel} htmlFor="type_bien">Type de bien</label>
          <select
            id="type_bien"
            className={inputBase}
            value={values.type_bien}
            onChange={handleField("type_bien")}
          >
            {TYPES_BIEN.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className={fieldLabel} htmlFor="surface_m2">Surface (m²)</label>
          <input
            id="surface_m2"
            type="number"
            min="1"
            max="2000"
            step="1"
            className={inputBase}
            value={values.surface_m2}
            onChange={handleField("surface_m2")}
          />
        </div>

        <div>
          <label className={fieldLabel} htmlFor="nb_pieces">Nombre de pièces</label>
          <input
            id="nb_pieces"
            type="number"
            min="1"
            max="20"
            step="1"
            className={inputBase}
            value={values.nb_pieces}
            onChange={handleField("nb_pieces")}
          />
        </div>

        <div>
          <label className={fieldLabel} htmlFor="nb_chambres">Nombre de chambres</label>
          <input
            id="nb_chambres"
            type="number"
            min="0"
            max="15"
            step="1"
            className={inputBase}
            value={values.nb_chambres}
            onChange={handleField("nb_chambres")}
          />
        </div>
      </div>

      <label className="flex w-fit cursor-pointer items-center gap-2.5 select-none">
        <input
          type="checkbox"
          checked={values.meuble}
          onChange={(e) => onChange("meuble", e.target.checked)}
          className="h-4 w-4 rounded border-brume-light text-argile focus:ring-argile/30"
        />
        <span className="text-[15px]">Le bien est meublé</span>
      </label>

      <fieldset>
        <legend className={fieldLabel}>Équipements</legend>
        <div className="flex flex-wrap gap-2">
          {EQUIPEMENTS.map((equip) => {
            const active = values.equipements.includes(equip.value);
            return (
              <button
                key={equip.value}
                type="button"
                onClick={() => toggleEquipement(equip.value)}
                aria-pressed={active}
                className={`rounded-full border px-3.5 py-1.5 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-argile/40 ${
                  active
                    ? "border-palmier bg-palmier text-sable"
                    : "border-brume-light bg-white text-encre hover:border-palmier/50"
                }`}
              >
                {equip.label}
              </button>
            );
          })}
        </div>
      </fieldset>

      {errors.length > 0 && (
        <div
          id="form-errors"
          role="alert"
          className="rounded-lg border border-argile/30 bg-argile/5 px-4 py-3 text-sm text-argile-dark"
        >
          <p className="font-medium">Le formulaire contient des erreurs :</p>
          <ul className="mt-1 list-inside list-disc">
            {errors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-lg bg-argile px-5 py-3 text-[15px] font-semibold text-sable transition-colors hover:bg-argile-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-argile/50 focus-visible:ring-offset-2 focus-visible:ring-offset-sable disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
      >
        {isSubmitting ? "Estimation en cours…" : "Estimer le loyer"}
      </button>
    </form>
  );
}
