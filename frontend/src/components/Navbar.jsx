import { Link } from "react-router-dom";
import Button from "./Button";
import "./Navbar.css";

/**
 * Top navigation bar shown on public pages (Landing, Login, Signup).
 * The logged-in area uses Sidebar.jsx instead.
 */
function Navbar() {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="navbar-brand-icon" aria-hidden="true">🩺</span>
          AI Health Assistant
        </Link>

        <nav className="navbar-links">
          <Link to="/login">Login</Link>
          <Link to="/signup">
            <Button variant="primary">Get Started</Button>
          </Link>
        </nav>
      </div>
    </header>
  );
}

export default Navbar;
