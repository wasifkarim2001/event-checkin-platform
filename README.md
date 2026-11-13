# Event Check-In Platform

> **Next time (updated 2026-11-12):** M0 to M2 are merged; M3 (React frontend) is in a pull request; M4 (deployment) is next. Local setup: Docker Desktop running, `.env` created from `.env.example`, then `docker compose up -d` starts the database, API and frontend.

> A web app where organizers create events, attendees register and get a check-in code, and staff check people in at the door while a dashboard shows live attendance. A small version of the kind of event software real companies run.

**Stack:** Python, Django, Django REST Framework, PostgreSQL, React, Docker Compose, pytest, GitHub Actions

**Status:** In progress. M0 (Docker, Django, PostgreSQL, `/health`, CI), M1 (data model), M2 (REST API) and M3 (React frontend) done. M4 (deployment) next.

## Why this project
Checking people in at an event looks simple until a line forms at the door. Several staff scan codes at once, the same ticket must never be accepted twice, and the organizer wants an attendance count they can trust in real time. Those are the same problems everyday business software has to handle: data integrity under concurrent writes, a clean API between the server and its clients, and a system that keeps running and can be diagnosed when something goes wrong.

The plan is to build it the way a small team would ship a production service, end to end. The milestone table below shows which parts are done so far.
- **Backend:** a REST API in Django and Django REST Framework on PostgreSQL, with database constraints that rule out a double check-in.
- **Frontend:** a React app for registration, the staff check-in screen and a live dashboard.
- **Quality:** automated tests with pytest, run by GitHub Actions on every pull request.
- **Operations:** Docker Compose for local development, structured logging, a health check endpoint and a cloud deployment.

## Features
**MVP**
- [x] Organizer login (token auth); roles per event: organizer (owner), staff
- [x] Create events with ticket types and capacity
- [x] Public registration endpoint; attendee gets a unique check-in code
- [x] Staff check-in screen: enter a code (a USB barcode scanner works as a keyboard), prevent double check-in
- [x] Live dashboard: registered vs. checked-in, per ticket type
- [ ] CSV import of attendees, CSV export of attendance

**Stretch**
- [ ] QR codes, email confirmation
- [ ] Waitlist when capacity is reached
- [ ] Offline-tolerant check-in screen

## Milestones (about 12 weeks at 6–8 hrs/week)
| # | Milestone | Skills | Target | Done |
|---|---|---|---|---|
| M0 | Repo, Docker Compose (Django + Postgres), first test, GitHub Actions running tests | Git workflow, Docker, CI, pytest | week 2 | ☑ |
| M1 | Data model (Event, TicketType, Attendee, CheckIn), migrations, admin, indexes | SQL, schema design, Django | week 4 | ☑ |
| M2 | REST API with auth, permissions, filtering, pagination, OpenAPI docs; 80%+ test coverage | DRF, REST design, TDD | week 6 | ☑ |
| M3 | React frontend: events, registration, check-in screen, dashboard | JS/TS, React | week 8 | ☑ |
| M4 | Logging, `/health`, Docker image, bash backup script, deploy to cloud, deploy workflow, write a post-mortem for a planted failure | Linux, logging, cloud, CI/CD, troubleshooting | week 10 | ☐ |
| M5 | Load test, CSV import/export, architecture diagram, demo, final README, resume bullets | Performance, docs, communication | week 12 | ☐ |

## Working agreement
- Work happens in small steps on feature branches, and every change goes through a pull request, even working alone.
- Who types the code depends on the milestone. Claude wrote M1 and M2. For M0 and M3 the student typed every file and ran every command: Claude gave each step's code with its "Why", then checked the result before the next step.
- Code comments stay short. The explanations live outside the code: after each file or code block comes a "Why" covering what it does, why it's written that way, which alternatives were considered, and the tradeoff. Design decisions (schema, constraints, indexes, API shape, auth, testing approach) get the same treatment.
- Explanations are pitched at a fourth-year CS undergrad: Django, DRF, PostgreSQL, Docker and CI specifics are explained, general programming basics are not.
- Each milestone ends with 3 to 5 interview questions it raises, with short, honest answers, so every part can be defended in an interview.
- Scope stays tight: each milestone does only what a working version needs, and anything cut is listed.
- Numbers in this README and on the resume come only from real measurements.

## How to run
Needs Docker Desktop.

```bash
cp .env.example .env        # then set your own local POSTGRES_PASSWORD
docker compose up -d        # starts PostgreSQL, Django and the React dev server
docker compose run --rm web python manage.py migrate
docker compose run --rm web pytest          # backend tests
docker compose exec frontend npm test       # frontend tests
```

The app is at http://localhost:5173 (staff sign-in at `/login`, public registration at `/events/<id>/register`). The API is at http://localhost:8000 and the health check at http://localhost:8000/health/.

To use the API, create a user (`docker compose run --rm web python manage.py createsuperuser`), then get a token with `POST /api/auth/token/` and send it as `Authorization: Token <token>`. Interactive API docs are at http://localhost:8000/api/docs/.

## API
| Method and path | Who | What |
|---|---|---|
| `POST /api/auth/token/` | anyone | Exchange username and password for a token |
| `GET, POST /api/events/` | signed in | List events you own or staff; create one (you become its owner) |
| `GET, PATCH, DELETE /api/events/{id}/` | owner (staff: read) | Event detail; owner sets `staff` by username |
| `GET, POST, PATCH, DELETE /api/ticket-types/` | owner (staff: read) | Ticket types and capacity; can't delete one with registrations |
| `GET /api/public/events/{id}/` | anyone | Event and remaining seats per ticket type |
| `POST /api/public/events/{id}/register/` | anyone | Register; returns the check-in code. 409 if sold out or email already registered |
| `POST /api/events/{id}/checkins/` | owner, staff | Check in by code. 409 with the original time if already checked in |
| `GET /api/events/{id}/attendees/` | owner, staff | Paginated list; `?search=` and `?checked_in=true/false` |
| `GET /api/events/{id}/stats/` | owner, staff | Capacity, registered and checked-in, per ticket type and total |

## Results (measured, not guessed)
- Test coverage: 100% line and branch coverage of application code (40 tests; migrations and test files excluded), measured 2026-11-11. CI fails below 80%.
- Frontend: 2 component tests (Vitest + React Testing Library) for the check-in screen; production bundle 84 kB gzipped, measured 2026-11-12.
- Load test (p95 latency at N concurrent users): 
- Records loaded: 

## What I learned / interview talking points
-

## Resume bullets (only after they're true)
-
