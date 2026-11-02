import { BrowserRouter, Routes, Route } from "react-router-dom";

import PublicLayout from "./layouts/PublicLayout";
import AppLayout from "./layouts/AppLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";
import Symptoms from "./pages/Symptoms";
import Profile from "./pages/Profile";
import Medicines from "./pages/Medicines";
import History from "./pages/History";

/**
 * All application routes are defined here.
 *
 * - PublicLayout wraps the Landing, Login, and Signup pages with the
 *   top Navbar.
 * - AppLayout wraps every logged-in page with the Sidebar.
 *
 * - ProtectedRoute redirects visitors without a login token to /login.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
        </Route>

        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/symptoms" element={<Symptoms />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/medicines" element={<Medicines />} />
          <Route path="/history" element={<History />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
