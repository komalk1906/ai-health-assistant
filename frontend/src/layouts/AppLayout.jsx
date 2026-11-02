import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "./AppLayout.css";

/**
 * Layout wrapper for all logged-in pages (Dashboard, Chat, Symptom
 * Checker, Profile, Medicines, History). Renders the Sidebar once,
 * so individual pages don't need to repeat navigation code.
 */
function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}

export default AppLayout;
