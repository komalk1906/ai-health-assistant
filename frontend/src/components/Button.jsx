import "./Button.css";

/**
 * Reusable button.
 * variant: "primary" | "secondary" | "ghost" | "danger"
 * Any other prop (onClick, type, disabled...) passes straight through.
 */
function Button({ children, variant = "primary", fullWidth = false, ...rest }) {
  const classNames = ["btn", `btn-${variant}`, fullWidth ? "btn-full" : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classNames} {...rest}>
      {children}
    </button>
  );
}

export default Button;
