import "./SymptomTag.css";

/**
 * A removable "chip" representing one symptom the user has added
 * to the symptom checker.
 */
function SymptomTag({ label, onRemove }) {
  return (
    <span className="symptom-tag">
      {label}
      <button
        type="button"
        className="symptom-tag-remove"
        onClick={onRemove}
        aria-label={`Remove ${label}`}
      >
        ×
      </button>
    </span>
  );
}

export default SymptomTag;
