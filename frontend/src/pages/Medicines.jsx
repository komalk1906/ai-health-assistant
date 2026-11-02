import { useEffect, useState } from "react";
import MedicineCard from "../components/MedicineCard";
import Alert from "../components/Alert";
import LoadingSpinner from "../components/LoadingSpinner";
import { getMedicines } from "../services/api";
import "./Medicines.css";

function Medicines() {
  const [query, setQuery] = useState("");
  const [medicines, setMedicines] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Calls GET /api/medicines?search=... shortly after the user stops typing
  // (the 300 ms delay avoids sending a request for every single keystroke).
  useEffect(() => {
    let cancelled = false;

    const timer = setTimeout(() => {
      getMedicines(query)
        .then((data) => {
          if (!cancelled) {
            setMedicines(data);
            setError("");
          }
        })
        .catch((err) => {
          if (!cancelled) setError(err.message);
        })
        .finally(() => {
          if (!cancelled) setIsLoading(false);
        });
    }, 300);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query]);

  // Show the spinner as soon as the user types (the effect above does the fetch)
  function handleSearchChange(e) {
    setQuery(e.target.value);
    setIsLoading(true);
  }

  return (
    <div className="medicines-page">
      <h1 className="page-title">Medicine Information</h1>
      <p className="page-subtitle">Search for general information about common medicines.</p>

      <Alert variant="warning">
        This information is educational only and does not provide personalized prescriptions or
        dosage recommendations. Always consult a qualified healthcare professional.
      </Alert>

      <input
        type="text"
        className="field-input medicines-search"
        placeholder="Search medicines (e.g. Paracetamol)"
        value={query}
        onChange={handleSearchChange}
        aria-label="Search medicines"
        maxLength={100}
      />

      {error && <Alert variant="danger">{error}</Alert>}

      {isLoading && <LoadingSpinner label="Loading medicines..." />}

      {!isLoading && !error && medicines.length === 0 && (
        <p className="medicines-empty">No medicines found for "{query}".</p>
      )}

      {!isLoading && !error && medicines.length > 0 && (
        <div className="medicines-grid">
          {medicines.map((medicine) => (
            <MedicineCard key={medicine.id} medicine={medicine} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Medicines;
