/**
 * src/services/api.js
 * ---------------------
 * This file is the ONLY place in the app that talks to the FastAPI backend.
 * Every page calls a function from here instead of calling fetch() directly,
 * so things like attaching the JWT token, reading error messages and handling
 * an expired login are written once.
 *
 * The base URL comes from an environment variable (see .env.example), so it
 * can be changed for local development vs. a deployed server without touching
 * any code.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOKEN_KEY = "authToken";
const USER_KEY = "authUser";

/* -----------------------------------------------------------
   SESSION HELPERS (JWT token + basic user info in localStorage)
----------------------------------------------------------- */

export function saveSession({ access_token, user }) {
  localStorage.setItem(TOKEN_KEY, access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isLoggedIn() {
  return Boolean(localStorage.getItem(TOKEN_KEY));
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY));
  } catch {
    return null;
  }
}

/* -----------------------------------------------------------
   GENERIC REQUEST HELPER
----------------------------------------------------------- */

/** Turn the backend's error JSON into one readable sentence. */
function readErrorMessage(body) {
  // Validation errors: { error: "Validation error", details: [{ loc, msg }] }
  if (Array.isArray(body.details) && body.details.length > 0) {
    const first = body.details[0];
    const field = Array.isArray(first.loc) ? first.loc[first.loc.length - 1] : "";
    return field ? `${field}: ${first.msg}` : first.msg;
  }
  // Normal errors: { detail: "Incorrect email or password." }
  if (typeof body.detail === "string") return body.detail;
  if (typeof body.error === "string") return body.error;
  return "Something went wrong. Please try again.";
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    // fetch() only throws when the server cannot be reached at all
    throw new Error(
      "Cannot reach the server. Please check that the backend is running and try again."
    );
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));

    // Logged-in user whose token expired or is invalid -> send them to login
    if (response.status === 401 && token && !endpoint.startsWith("/api/auth/login")) {
      clearSession();
      window.location.assign("/login");
    }

    const error = new Error(readErrorMessage(body));
    error.status = response.status;
    throw error;
  }

  return response.json();
}

/* -----------------------------------------------------------
   AUTHENTICATION  (/api/auth/*)
----------------------------------------------------------- */

export function registerUser(payload) {
  // payload: { full_name, email, password, age, gender }
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  // payload: { email, password }
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getCurrentUser() {
  return request("/api/auth/me");
}

export async function logoutUser() {
  // The backend logout is stateless (it only confirms), so even if this call
  // fails we still clear the local session.
  try {
    await request("/api/auth/logout", { method: "POST" });
  } catch {
    /* ignore */
  } finally {
    clearSession();
  }
}

/* -----------------------------------------------------------
   HEALTH PROFILE  (/api/health/profile)
----------------------------------------------------------- */

export function getHealthProfile() {
  return request("/api/health/profile");
}

export function createHealthProfile(payload) {
  return request("/api/health/profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateHealthProfile(payload) {
  return request("/api/health/profile", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

/* -----------------------------------------------------------
   AI CHAT  (/api/chat)
----------------------------------------------------------- */

export function sendChatMessage(message) {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

/* -----------------------------------------------------------
   SYMPTOM CHECKER  (/api/symptoms/check)
----------------------------------------------------------- */

export function checkSymptoms(symptoms) {
  return request("/api/symptoms/check", {
    method: "POST",
    body: JSON.stringify({ symptoms }),
  });
}

/* -----------------------------------------------------------
   MEDICINE INFORMATION  (/api/medicines)
----------------------------------------------------------- */

export function getMedicines(search = "") {
  const query = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : "";
  return request(`/api/medicines${query}`);
}

export function getMedicineInfo(medicineName) {
  return request(`/api/medicines/${encodeURIComponent(medicineName)}`);
}

/* -----------------------------------------------------------
   HEALTH HISTORY  (/api/history)
----------------------------------------------------------- */

export function getHistory() {
  return request("/api/history");
}
