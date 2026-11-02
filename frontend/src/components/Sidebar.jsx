import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { logoutUser } from "../services/api";
import "./Sidebar.css";

/**
 * Sidebar navigation for all logged-in pages (Dashboard, Chat,
 * Symptom Checker, Profile, Medicines, History).
 * Collapses into a top bar with a toggle button on mobile.
 */
const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "🏠" },
  { to: "/chat", label: "AI Chat", icon: "💬" },
  { to: "/symptoms", label: "Symptom Checker", icon: "🩺" },
  { to: "/profile", label: "Health Profile", icon: "📋" },
  { to: "/medicines", label: "Medicines", icon: "💊" },
  { to: "/history", label: "History", icon: "🕘" },
];

function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  async function handleLogout() {
    await logoutUser();
    navigate("/login");
  }

  return (
    <>
      <div className="sidebar-topbar">
        <span className="sidebar-brand">🩺 AI Health Assistant</span>
        <button
          className="sidebar-toggle"
          onClick={() => setIsOpen((v) => !v)}
          aria-label="Toggle navigation menu"
          aria-expanded={isOpen}
        >
          ☰
        </button>
      </div>

      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-brand sidebar-brand-desktop">
          🩺 AI Health Assistant
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "sidebar-link-active" : ""}`
              }
              onClick={() => setIsOpen(false)}
            >
              <span aria-hidden="true">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button className="sidebar-logout" onClick={handleLogout}>
          <span aria-hidden="true">🚪</span>
          Logout
        </button>
      </aside>
    </>
  );
}

export default Sidebar;
