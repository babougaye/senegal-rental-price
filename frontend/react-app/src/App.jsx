import { useState } from "react";
import BrandPanel from "./components/BrandPanel";
import RentalForm from "./components/RentalForm";
import ResultCard from "./components/ResultCard";
import { predictPrice } from "./api";

const initialValues = {
  ville: "Dakar",
  quartier: "",
  type_bien: "appartement",
  surface_m2: 80,
  nb_pieces: 3,
  nb_chambres: 2,
  meuble: false,
  equipements: [],
};

function validate(values) {
  const errors = [];
  if (!values.surface_m2 || values.surface_m2 <= 0 || values.surface_m2 > 2000) {
    errors.push("La surface doit être comprise entre 1 et 2000 m².");
  }
  if (!values.nb_pieces || values.nb_pieces < 1 || values.nb_pieces > 20) {
    errors.push("Le nombre de pièces doit être compris entre 1 et 20.");
  }
  if (values.nb_chambres === "" || values.nb_chambres < 0 || values.nb_chambres > 15) {
    errors.push("Le nombre de chambres doit être compris entre 0 et 15.");
  }
  if (Number(values.nb_chambres) > Number(values.nb_pieces)) {
    errors.push("Le nombre de chambres ne peut pas dépasser le nombre de pièces.");
  }
  return errors;
}

export default function App() {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState([]);
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [submittedContext, setSubmittedContext] = useState({ ville: "Dakar", surface: 80 });

  const handleChange = (field, value) => {
    setValues((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate(values);
    setErrors(validationErrors);
    if (validationErrors.length > 0) return;

    setStatus("loading");
    setErrorMessage("");

    try {
      const payload = {
        ...values,
        quartier: values.quartier.trim() === "" ? null : values.quartier.trim(),
      };
      const data = await predictPrice(payload);
      setResult(data);
      setSubmittedContext({ ville: values.ville, surface: values.surface_m2 });
      setStatus("success");
    } catch (err) {
      setStatus("error");
      if (err.status === 422 && Array.isArray(err.details)) {
        setErrorMessage(
          "L'API a rejeté certaines valeurs : " +
            err.details.map((d) => d.msg).join(" · ")
        );
      } else {
        setErrorMessage(
          "Impossible de contacter le service de prédiction. Vérifiez que l'API est démarrée."
        );
      }
    }
  };

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <BrandPanel />

      <main className="flex-1 px-6 py-10 sm:px-10 md:px-14 md:py-14">
        <div className="mx-auto grid max-w-4xl gap-10 lg:grid-cols-[1fr_320px]">
          <RentalForm
            values={values}
            errors={errors}
            onChange={handleChange}
            onSubmit={handleSubmit}
            isSubmitting={status === "loading"}
          />

          <ResultCard
            result={result}
            status={status}
            errorMessage={errorMessage}
            ville={submittedContext.ville}
            surface={submittedContext.surface}
          />
        </div>
      </main>
    </div>
  );
}
