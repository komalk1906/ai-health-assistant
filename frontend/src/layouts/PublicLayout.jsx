import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

/**
 * Layout wrapper for public-facing pages (Landing, Login, Signup).
 * Renders the top Navbar, then whichever page matched the route
 * via <Outlet />.
 */
function PublicLayout() {
  return (
    <div>
      <Navbar />
      <Outlet />
    </div>
  );
}

export default PublicLayout;
