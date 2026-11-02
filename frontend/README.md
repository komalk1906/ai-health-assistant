# AI Health Assistant — Frontend

A React + Vite frontend for a TYBSc Computer Science mini project. This is
the UI layer only — it is built to later connect to a separate FastAPI +
SQLite backend through REST APIs. All data shown right now (dashboard
stats, medicines, history) is **sample data**, ready to be replaced with
real API calls.

## Technology
- React (JavaScript, no TypeScript)
- Vite
- React Router (page navigation)
- Plain CSS (no UI framework), using CSS variables for a consistent theme

## Folder Structure
```
ai-health-assistant-frontend/
│
├── src/
│   ├── components/     → Small reusable UI pieces (Button, Card, Modal, etc.)
│   ├── pages/           → One file per route/screen (Landing, Login, Chat, etc.)
│   ├── layouts/         → Page "shells" - PublicLayout (Navbar) and AppLayout (Sidebar)
│   ├── services/        → api.js - the only file that will talk to the backend
│   ├── assets/          → Images
│   ├── App.jsx          → All routes are defined here
│   ├── main.jsx         → React's entry point
│   └── index.css        → Global styles and design tokens (colors, fonts, spacing)
│
├── public/
├── .env.example         → Sample environment variable file
├── package.json
└── README.md
```

## Installation
```bash
npm install
```

## Environment Setup
Copy the example env file:
```bash
copy .env.example .env      # Windows
cp .env.example .env        # Mac/Linux
```
It contains one variable:
```
VITE_API_URL=http://localhost:8000
```
This will be the address of your FastAPI backend once it's connected.

## Running the app
```bash
npm run dev
```
Then open the local URL shown in the terminal (usually `http://localhost:5173`).

## Pages & Routes
| Route         | Page              | Layout        |
|---------------|-------------------|---------------|
| `/`           | Landing           | Public (Navbar) |
| `/login`      | Login             | Public (Navbar) |
| `/signup`     | Signup            | Public (Navbar) |
| `/dashboard`  | Dashboard         | App (Sidebar) |
| `/chat`       | AI Health Chat    | App (Sidebar) |
| `/symptoms`   | Symptom Checker   | App (Sidebar) |
| `/profile`    | Health Profile    | App (Sidebar) |
| `/medicines`  | Medicine Information | App (Sidebar) |
| `/history`    | Health History    | App (Sidebar) |

## How React Router works here
`App.jsx` defines two groups of routes, each wrapped in a **layout**:
- Routes inside `<Route element={<PublicLayout />}>` share the top Navbar.
- Routes inside `<Route element={<AppLayout />}>` share the Sidebar.

Each layout uses React Router's `<Outlet />` component, which is where the
matching page actually renders. This avoids repeating the Navbar/Sidebar
code in every single page.

There is currently no login "guard" (no redirect if you're not logged
in) since there's no backend yet to check against. Once auth is
connected, a `ProtectedRoute` wrapper can be added around the `AppLayout`
routes.

## How this will connect to the FastAPI backend later
Every page that needs real data already imports (or will import)
functions from `src/services/api.js` — for example `loginUser()`,
`sendChatMessage()`, `checkSymptoms()`, `getHistory()`, etc. Each of
these functions is already written to call the matching FastAPI endpoint
using `fetch()`, and automatically attaches a JWT token (once login is
implemented) from `localStorage`.

The flow will look like this:
```
React component  →  services/api.js  →  FastAPI backend  →  SQLite / AI service
```

To connect a page for real, you'll:
1. Import the relevant function from `services/api.js` into the page.
2. Replace the `setTimeout(...)` placeholder logic with a real call to
   that function (usually inside an `async` handler).
3. Use the real response instead of the sample data.

No page currently calls the backend — this keeps Task boundaries clean
so the frontend can be demoed and explained on its own first.

## Design system
All colors, fonts, and spacing are defined once as CSS variables in
`src/index.css`, under `:root`. Every component/page references these
variables (e.g. `var(--color-primary)`) instead of hardcoding colors, so
the whole theme can be changed from one place.

## Accessibility notes
- All form fields have associated `<label>` elements
- Buttons and links have descriptive/aria labels where needed (e.g. "Remove headache" on symptom chips)
- Keyboard focus is visible on all interactive elements
- Color contrast follows WCAG-friendly combinations

## Medical safety
Every page that involves health information (Chat, Symptom Checker,
Medicines) includes a visible disclaimer that this application does not
diagnose conditions and is not a substitute for professional medical
advice.
