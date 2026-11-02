import "./Input.css";

/**
 * Reusable labeled input field with built-in error message display.
 * Works for text, email, password, number, etc. via the `type` prop,
 * and can render a <select> instead when `options` is provided.
 */
function Input({ label, id, error, options, ...rest }) {
  return (
    <div className="field">
      <label htmlFor={id} className="field-label">
        {label}
      </label>

      {options ? (
        <select id={id} className={`field-input ${error ? "field-input-error" : ""}`} {...rest}>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          id={id}
          className={`field-input ${error ? "field-input-error" : ""}`}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${id}-error` : undefined}
          {...rest}
        />
      )}

      {error && (
        <p className="field-error" id={`${id}-error`}>
          {error}
        </p>
      )}
    </div>
  );
}

export default Input;
