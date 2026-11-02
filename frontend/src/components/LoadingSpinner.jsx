import "./LoadingSpinner.css";

/**
 * Small inline loading spinner, used while waiting for the (future)
 * AI or symptom-checker responses.
 */
function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <span className="spinner" />
      <span className="spinner-label">{label}</span>
    </div>
  );
}

export default LoadingSpinner;
