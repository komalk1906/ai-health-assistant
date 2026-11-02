import "./Alert.css";

/**
 * Alert / banner message used for form errors, warnings, and the
 * medical-safety disclaimers shown throughout the app.
 * variant: "info" | "warning" | "danger" | "success"
 */
function Alert({ variant = "info", children }) {
  return (
    <div className={`alert alert-${variant}`} role="status">
      {children}
    </div>
  );
}

export default Alert;
