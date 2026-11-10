# AudienceFlow — Frontend

React + Vite frontend for the AudienceFlow platform.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 18 |
| Build tool | Vite 5 |
| Routing | React Router DOM v6 |
| HTTP client | Axios |
| Icons | Lucide React |
| Styling | CSS (custom design system) |
| Fonts | Google Fonts — Inter |

## Project Structure

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── assets/              # Static assets
│   ├── components/
│   │   ├── Navbar.jsx       # Sticky navbar with mobile hamburger
│   │   ├── Footer.jsx       # Footer with link columns
│   │   ├── FeatureCard.jsx  # Reusable feature card
│   │   └── StepCard.jsx     # Numbered workflow step card
│   ├── layouts/
│   │   └── MainLayout.jsx   # Navbar + content + Footer wrapper
│   ├── pages/
│   │   ├── LandingPage.jsx  # Full landing page with all sections
│   │   ├── LoginPage.jsx    # Login form with validation
│   │   └── RegisterPage.jsx # Register form with validation
│   ├── services/
│   │   └── api.js           # Axios instance + checkHealth()
│   ├── styles/
│   │   ├── global.css       # Design tokens, reset, utilities
│   │   └── landing.css      # Landing page + auth page styles
│   ├── App.jsx              # Router + health check hook
│   └── main.jsx             # React DOM entry point
├── .env.example
├── index.html
├── package.json
└── vite.config.js
```

## Prerequisites

- Node.js 18+
- npm 9+

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment variables

```bash
cp .env.example .env
# .env is pre-configured for local development — no changes needed
```

### 3. Start the development server

```bash
npm run dev
```

The frontend runs at **http://localhost:5173**.

### 4. Build for production

```bash
npm run build
npm run preview   # Preview the production build locally
```

## Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | LandingPage | Hero, Features, How It Works, CTA |
| `/login` | LoginPage | Email + password form with validation |
| `/register` | RegisterPage | Full registration form with strength meter |

## API Integration

`src/services/api.js` provides:

- A configured Axios instance reading `VITE_API_BASE_URL`
- `checkHealth()` — calls `GET /health` on the backend
- Request/response interceptors for logging

The `App.jsx` calls `checkHealth()` on mount and passes the status to `LandingPage`,
which displays a small API connectivity badge in the hero section.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | FastAPI backend URL | `http://localhost:8000` |

> Only variables prefixed with `VITE_` are exposed to the browser bundle.
> Never put secret keys in frontend environment variables.

## Troubleshooting

**Port 5173 already in use**
Change the port in `vite.config.js` → `server.port`.

**API badge shows "API Offline"**
Make sure the FastAPI backend is running on port 8000 and CORS is configured for `http://localhost:5173`.

**`lucide-react` import errors**
Run `npm install` to ensure all packages are installed.
