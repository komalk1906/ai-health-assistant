import { useState } from "react";
import Card from "../components/Card";
import Button from "../components/Button";
import SymptomTag from "../components/SymptomTag";
import LoadingSpinner from "../components/LoadingSpinner";
import Alert from "../components/Alert";
import { checkSymptoms } from "../services/api";
import "./Symptoms.css";

function Symptoms() {
  const [symptomInput, setSymptomInput] = useState("");
  const [symptoms, setSymptoms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function handleAddSymptom(e) {
    e.preventDefault();
    const trimmed = symptomInput.trim();
    if (!trimmed) return;
    if (symptoms.includes(trimmed)) {
      setSymptomInput("");
      return;
    }
    setSymptoms((prev) => [...prev, trimmed]);
    setSymptomInput("");
  }

  function handleRemoveSymptom(symptomToRemove) {
    setSymptoms((prev) => prev.filter((s) => s !== symptomToRemove));
  }

  async function handleCheckSymptoms() {
    if (symptoms.length === 0) return;
    setIsLoading(true);
    setResult(null);
    setError("");

    try {
      // POST /api/symptoms/check
      const data = await checkSymptoms(symptoms);
      setResult({
        explanations: data.possible_explanations,
        severity: data.severity,
        advice: data.advice,
        recommend: data.professional_attention_recommended
          ? "Based on these symptoms, it is a good idea to speak with a healthcare professional."
          : "If symptoms persist beyond a few days or worsen, consult a healthcare professional.",
        isEmergency: data.is_emergency,
        emergencyMessage: data.emergency_message,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="symptoms-page">
      <h1 className="page-title">Symptom Checker</h1>
      <p className="page-subtitle">Add your symptoms below to get general information.</p>

      <Alert variant="warning">
        This tool does not provide a medical diagnosis. It offers general information only -
        always consult a qualified healthcare professional for medical concerns.
      </Alert>

      <Card>
        <form className="symptom-form" onSubmit={handleAddSymptom}>
          <label htmlFor="symptom-input" className="field-label">
            Add a symptom
          </label>
          <div className="symptom-input-row">
            <input
              id="symptom-input"
              type="text"
              className="field-input"
              placeholder="e.g. headache, fever, fatigue"
              value={symptomInput}
              onChange={(e) => setSymptomInput(e.target.value)}
            />
            <Button type="submit" variant="secondary">
              Add
            </Button>
          </div>
        </form>

        {symptoms.length > 0 && (
          <div className="symptom-chips">
            {symptoms.map((symptom) => (
              <SymptomTag
                key={symptom}
                label={symptom}
                onRemove={() => handleRemoveSymptom(symptom)}
              />
            ))}
          </div>
        )}

        <Button
          onClick={handleCheckSymptoms}
          disabled={symptoms.length === 0 || isLoading}
          fullWidth
        >
          Check Symptoms
        </Button>
      </Card>

      {error && <Alert variant="danger">{error}</Alert>}

      {isLoading && (
        <div className="symptoms-loading">
          <LoadingSpinner label="Analyzing symptoms..." />
        </div>
      )}

      {result && !isLoading && (
        <Card className="symptoms-result">
          <h2 className="result-heading">Results</h2>

          {result.isEmergency && result.emergencyMessage && (
            <Alert variant="danger">{result.emergencyMessage}</Alert>
          )}

          <div className={`severity-badge severity-${result.severity.toLowerCase()}`}>
            Severity: {result.severity}
          </div>

          <div className="result-section">
            <h3>Possible general explanations</h3>
            <p>{result.explanations}</p>
          </div>

          <div className="result-section">
            <h3>General advice</h3>
            <p>{result.advice}</p>
          </div>

          <Alert variant="info">{result.recommend}</Alert>

          <p className="result-disclaimer">
            This is not a medical diagnosis. Please consult a qualified healthcare professional
            for an accurate assessment.
          </p>
        </Card>
      )}
    </div>
  );
}

export default Symptoms;
