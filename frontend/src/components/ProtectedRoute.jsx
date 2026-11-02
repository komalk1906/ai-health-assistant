import { Navigate } from "react-router-dom";
import { isLoggedIn } from "../services/api";

/**
 * Wraps the logged-in pages. If there is no saved login token, the visitor
 * is sent to /login instead of seeing an empty dashboard.
 */
function ProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default ProtectedRoute;
