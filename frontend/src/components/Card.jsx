import "./Card.css";

/**
 * Simple reusable card container with consistent padding, radius and shadow.
 * Extra className can be passed to add page-specific tweaks.
 */
function Card({ children, className = "", ...rest }) {
  return (
    <div className={`card ${className}`} {...rest}>
      {children}
    </div>
  );
}

export default Card;
