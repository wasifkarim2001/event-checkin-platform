# Event Check-In Platform

A web app where organizers create events, attendees register and get a check-in code, and staff check people in at the door while a dashboard shows live attendance.

**Live:** https://event-checkin-platform.onrender.com (free tier: the first request after 15 idle minutes takes about 35 s while the app and database wake up) · **API docs:** [/api/docs/](https://event-checkin-platform.onrender.com/api/docs/)

**Stack:** Python, Django, Django REST Framework, PostgreSQL, React + TypeScript (Vite), Docker, pytest, Vitest, GitHub Actions, Render, Neon

## Why this project
Checking people in looks simple until a line forms at the door. Several staff scan codes at once, the same ticket must never be accepted twice, the last seat must not be sold twice, and the organizer wants a count they can trust in real time. Those are the problems everyday business software has: data integrity under concurrent writes, a clean API, and a service that can be deployed, backed up and diagnosed.

## Features
- Organizer sign-in with expiring tokens; per-event roles: owner and staff
- Events with ticket types and capacity
- Public registration page; each attendee gets a unique check-in code
- Staff check-in screen (a USB barcode scanner works as a keyboard), with double check-in refused
- Live dashboard: registered vs. checked in, per ticket type

## Architecture

```
Browser ──► Cloudflare ──► Render (one Docker container)              Neon
                           gunicorn ─► Django + DRF  ──────────────►  PostgreSQL 17
                                       WhiteNoise serves the React build

GitHub Actions
  CI       every PR and push: tests, migration check, OpenAPI check, deploy-settings check,
           backup + restore drill, production image build
  Deploy   after CI passes on main: deploy that exact commit, wait until /health/ reports it, smoke test
  Backup   daily: pg_dump ─► gpg (AES-256) ─► artifact kept 14 days
```

## Engineering decisions
- **No double check-in, enforced by the database.** `CheckIn.attendee` is one-to-one, so PostgreSQL rejects a second row. The insert runs in a savepoint; the `IntegrityError` becomes a 409 with the time of the first check-in. A test fires two check-ins from parallel threads and expects exactly one to win.
- **No overselling.** Registration locks the event row (`SELECT ... FOR UPDATE`), so the capacity count and the duplicate-email check can't race. Emails are unique per ticket type, case-insensitively, through a `UNIQUE (ticket_type, lower(email))` constraint. Also tested with parallel threads.
- **Auth and abuse limits.** DRF tokens expire after 12 hours, sign-out deletes the token on the server, and an expired token is replaced at the next sign-in. Rate limits: 5 sign-ins per minute and 20 registrations per hour per client IP. The client IP comes from `X-Forwarded-For` with `NUM_PROXIES=3`, a value I measured from the live request chain (client, Cloudflare, Render) rather than guessed, so a spoofed header can't reset the limit.
- **Production settings from the environment.** A missing secret stops the app at startup. HTTPS redirect, HSTS and Secure cookies are on, and CI fails if `manage.py check --deploy` reports any warning.
- **Observability.** Logs are JSON on stdout, one line per request with method, path, status, duration and user, plus business events (registration created or rejected with the reason, checked in). Every request gets an ID, returned in the `X-Request-ID` header and attached to every log line it causes. Events are logged after the transaction commits, so a rolled-back write is never reported as done. `/health/` checks the database (503 if unreachable) and reports the running commit.
- **One production image.** A multi-stage Dockerfile builds the React app with Node and copies only the output into a slim Python image. Django serves the API and admin; WhiteNoise serves the pre-compressed React build with hashed asset names cached as immutable, and any other path falls back to `index.html` for client-side routing. Runs as a non-root user.
- **Deploys you can trust.** The deploy workflow asks Render for the exact commit CI tested, then polls `/health/` until that commit is serving, because during a build the old version still answers 200.
- **Backups that are restored, not just taken.** A daily workflow dumps the database with `pg_dump` 17, encrypts it with a passphrase (the repository is public and artifacts are downloadable), checks that it decrypts, and keeps it for 14 days. CI restores a fresh backup into an empty database on every run; the production backup was restored locally and its row counts matched production.

## Results (measured)
- **Tests:** 58 backend tests at 100% line and branch coverage of application code (CI fails below 80%), plus 2 frontend component tests.
- **Production image:** 292 MB on disk, 63.1 MB compressed.
- **Frontend:** main JavaScript bundle 83 kB gzipped (267 kB uncompressed), as served by the live site.
- **Response time of `/health/` on the free tier:** about 0.15 s warm (3 samples, 0.14–0.19 s); 34.4 s on a cold start (1 sample).
- **Deploy:** from merge to the new commit serving took about a minute on the first automated deploy.
- **Backup:** a 52 kB dump becomes a 9.2 kB encrypted artifact.

Numbers are from November 2026 on the free tiers of Render and Neon.

## Run it locally
Needs Docker Desktop.

```bash
cp .env.example .env        # then set your own POSTGRES_PASSWORD and DJANGO_SECRET_KEY
docker compose up -d        # PostgreSQL, Django (dev server) and the React dev server
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose run --rm web pytest          # backend tests
docker compose exec frontend npm test       # frontend tests
```

The app is at http://localhost:5173 (staff sign-in at `/login`, public registration at `/events/<id>/register`). Create events and ticket types in the Django admin at http://localhost:8000/admin/. API docs are at http://localhost:8000/api/docs/.

To build and run the production image: `docker build -t checkin .`

## API
| Method and path | Who | What |
|---|---|---|
| `POST /api/auth/token/` | anyone | Exchange username and password for a token |
| `POST /api/auth/logout/` | signed in | Delete the current token |
| `GET, POST /api/events/` | signed in | List events you own or staff; create one (you become its owner) |
| `GET, PATCH, DELETE /api/events/{id}/` | owner (staff: read) | Event detail; owner sets `staff` by username |
| `GET, POST, PATCH, DELETE /api/ticket-types/` | owner (staff: read) | Ticket types and capacity; can't delete one with registrations |
| `GET /api/public/events/{id}/` | anyone | Event and remaining seats per ticket type |
| `POST /api/public/events/{id}/register/` | anyone | Register; returns the check-in code. 409 if sold out or email already registered |
| `POST /api/events/{id}/checkins/` | owner, staff | Check in by code. 409 with the original time if already checked in |
| `GET /api/events/{id}/attendees/` | owner, staff | Paginated list; `?search=` and `?checked_in=true/false` |
| `GET /api/events/{id}/stats/` | owner, staff | Capacity, registered and checked in, per ticket type and total |

## Scope

**Deliberately cut so far:** tokens in HttpOnly cookies (tokens live in `localStorage`), a planted-failure post-mortem, CSV import and export, a load test, QR codes and email confirmation, a waitlist, an offline check-in mode.

**Known limits:** the free tier sleeps after 15 idle minutes; GitHub pauses scheduled workflows after 60 days without commits, which would stop the daily backup; the rate limit trusts the proxy chain's `X-Forwarded-For` (Cloudflare's `CF-Connecting-IP` would be simpler).

## License
[MIT](LICENSE)
