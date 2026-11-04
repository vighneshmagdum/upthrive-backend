# UpThrive

UpThrive is a career-growth dashboard with account authentication, an editable skill and goal profile, and personalized career-path and learning-plan recommendations.

This repository started as a Spring Boot authentication and user CRUD service. The original Java implementation remains in place. This branch adds a separate FastAPI service and a Next.js web dashboard, plus PostgreSQL migrations and a Docker deployment layout.

## Run locally

1. Copy .env.example to .env.
2. For a public deployment, replace JWT_SECRET and POSTGRES_PASSWORD with strong unique values, set ENVIRONMENT=production, set AUTH_COOKIE_SECURE=true, and set APP_DOMAIN to the HTTPS hostname.
3. Start the stack with docker compose up --build.
4. Open http://localhost for the dashboard. The API documentation is at http://localhost/api/v1/docs.

The compose stack starts PostgreSQL, runs Alembic migrations before FastAPI, starts the Next.js server, and routes traffic through Caddy. Caddy provisions TLS automatically when APP_DOMAIN is set to a real domain whose DNS points to the host and ports 80/443 are reachable.

The local values in .env.example are for development only. Do not deploy them publicly.

## Free hosted demo (Render + Neon)

The `render.yaml` Blueprint deploys the Next.js dashboard and FastAPI API together as one Render web service. The frontend is built as a static export and FastAPI serves it on the same origin, so browser API calls and the HttpOnly authentication cookies stay same-origin. PostgreSQL is hosted separately on Neon so database files do not live on Render's ephemeral service disk.

To deploy, create a Neon PostgreSQL project, copy its pooled connection string, and create a Render Blueprint from the `codex/upthrive-fullstack-fastapi-nextjs` branch. Set the Blueprint's `DATABASE_URL` to the Neon connection string; Render generates `JWT_SECRET`. Keep `AUTH_COOKIE_SECURE=true` for the HTTPS service. The app runs Alembic migrations before starting FastAPI.

Render's free web service can sleep after inactivity, so the first request after a quiet period may take longer. Neon free-tier limits and availability can change; check the provider's current plan before relying on a demo for production data.

## Services

| Service | Path | Responsibility |
|---|---|---|
| FastAPI | backend/app | Authentication, account profile, recommendation API, and health checks |
| Next.js | frontend | Responsive dashboard and sign-in/create-account experience |
| PostgreSQL | Compose service | Accounts, profiles, refresh sessions, and saved/completed recommendations |
| Caddy | Caddyfile | Same-origin routing and automatic HTTPS on a configured domain |
| Existing Spring Boot app | src/main/java | Original JWT user authentication and CRUD baseline |

## Authentication

The original Java request flow and credential handling are documented in docs/authentication.md, with direct links to the source classes. The new FastAPI flow uses Argon2id password hashes, short-lived access cookies, rotating opaque refresh tokens stored as hashes, and CSRF checks. Credentials and signing secrets come from environment variables.

## Recommendation engine

The FastAPI recommendation service ranks career paths against profile skills, interests, goals, experience level, and weekly study time. It uses a transparent TF-IDF and cosine-similarity model with explicit profile-fit signals, and returns a short reason for each result. This is an implemented local model; it does not call an external LLM or claim to be trained on private user data. The catalog is in backend/app/recommendations/catalog.py and scoring logic is in backend/app/recommendations/engine.py.

## API routes

All routes are prefixed with /api/v1.

| Method | Route | Purpose |
|---|---|---|
| GET | /auth/csrf | Issue the CSRF cookie and token |
| POST | /auth/register | Create an account and sign in |
| POST | /auth/login | Sign in |
| POST | /auth/refresh | Rotate the refresh token and renew access |
| POST | /auth/logout | Revoke the current refresh session |
| GET | /users/me | Read account and growth profile |
| PATCH | /users/me/profile | Update role, skills, interests, goals, level, and study time |
| GET | /recommendations | Get ranked career paths and learning plans |
| PATCH | /recommendations/{id}/status | Save, complete, or dismiss a recommendation |
| GET | /health/live, /health/ready | Container liveness and database readiness |

## Development

For direct local API development, copy .env.example to backend/.env, edit DATABASE_URL to point at a local PostgreSQL instance, then run these commands from backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Run the dashboard separately from frontend with npm install and npm run dev. Set API_INTERNAL_URL=http://localhost:8000 so the Next.js rewrite forwards /api/* requests to FastAPI.

