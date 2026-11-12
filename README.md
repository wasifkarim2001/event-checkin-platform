# Event Check-In Platform

> **Next time (updated 2026-11-11):** M0 is merged. M1 (data model) is in progress on a feature branch. Local setup: Docker Desktop running, `.env` created from `.env.example`, `docker compose run --rm web pytest` passing.

> A web app where organizers create events, attendees register and get a check-in code, and staff check people in at the door while a dashboard shows live attendance. A small version of the kind of event software real companies run.

**Stack:** Python, Django, Django REST Framework, PostgreSQL, React, Docker Compose, pytest, GitHub Actions

**Status:** In progress. M0 (Docker, Django, PostgreSQL, `/health`, CI) and M1 (data model) done. M2 (REST API) next.

## Why this project
Checking people in at an event looks simple until a line forms at the door. Several staff scan codes at once, the same ticket must never be accepted twice, and the organizer wants an attendance count they can trust in real time. Those are the same problems everyday business software has to handle: data integrity under concurrent writes, a clean API between the server and its clients, and a system that keeps running and can be diagnosed when something goes wrong.

The plan is to build it the way a small team would ship a production service, end to end. The milestone table below shows which parts are done so far.
- **Backend:** a REST API in Django and Django REST Framework on PostgreSQL, with database constraints that rule out a double check-in.
- **Frontend:** a React app for registration, the staff check-in screen and a live dashboard.
- **Quality:** automated tests with pytest, run by GitHub Actions on every pull request.
- **Operations:** Docker Compose for local development, structured logging, a health check endpoint and a cloud deployment.

## Features
**MVP**
- [ ] Organizer login (token/JWT auth); roles: organizer, staff
- [ ] Create events with ticket types and capacity
- [ ] Public registration endpoint; attendee gets a unique check-in code
- [ ] Staff check-in screen: enter or scan a code, prevent double check-in
- [ ] Live dashboard: registered vs. checked-in, per ticket type
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
| M2 | REST API with auth, permissions, filtering, pagination, OpenAPI docs; 80%+ test coverage | DRF, REST design, TDD | week 6 | ☐ |
| M3 | React frontend: events, registration, check-in screen, dashboard | JS/TS, React | week 8 | ☐ |
| M4 | Logging, `/health`, Docker image, bash backup script, deploy to cloud, deploy workflow, write a post-mortem for a planted failure | Linux, logging, cloud, CI/CD, troubleshooting | week 10 | ☐ |
| M5 | Load test, CSV import/export, architecture diagram, demo, final README, resume bullets | Performance, docs, communication | week 12 | ☐ |

## Working agreement
- Claude writes the code in small steps on feature branches, and every change goes through a pull request, even working alone.
- Code comments stay short. The explanations live outside the code: after each file or code block comes a "Why" covering what it does, why it's written that way, which alternatives were considered, and the tradeoff. Design decisions (schema, constraints, indexes, API shape, auth, testing approach) get the same treatment.
- Explanations are pitched at a fourth-year CS undergrad: Django, DRF, PostgreSQL, Docker and CI specifics are explained, general programming basics are not.
- Each milestone ends with 3 to 5 interview questions it raises, with short, honest answers, so every part can be defended in an interview.
- Scope stays tight: each milestone does only what a working version needs, and anything cut is listed.
- Numbers in this README and on the resume come only from real measurements.

## How to run
Needs Docker Desktop.

```bash
cp .env.example .env        # then set your own local POSTGRES_PASSWORD
docker compose up -d        # starts PostgreSQL and Django
docker compose run --rm web python manage.py migrate
docker compose run --rm web pytest
```

The app is at http://localhost:8000 and the health check at http://localhost:8000/health/.

## Results (measured, not guessed)
- Test coverage: 
- Load test (p95 latency at N concurrent users): 
- Records loaded: 

## What I learned / interview talking points
-

## Resume bullets (only after they're true)
-
