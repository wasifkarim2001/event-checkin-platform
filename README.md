# Event Check-In Platform

> **Next time (updated 2026-11-09):** Setup is done on the PC (Python 3.14 via `py -3.14`, Git, gh, Docker Desktop on WSL2, all checked). Milestones M0 to M5 exist on GitHub. Resume at **M0 step 0**: create the 6 M0 issues with `gh issue create ... --milestone "M0: Setup, Docker, CI"` in the VS Code terminal at `Z:\event-checkin-platform`, then step 1 (feature branch, `.gitignore`, `.gitattributes`, `.env.example`).

> A web app where organizers create events, attendees register and get a check-in code, and staff check people in at the door while a dashboard shows live attendance. A small version of the kind of event software real companies run.

**Stack:** Python, Django, Django REST Framework, PostgreSQL, React, Docker Compose, pytest, GitHub Actions
**Status:** M0 in progress (dev setup done, milestones created).

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
| M0 | Repo, Docker Compose (Django + Postgres), first test, GitHub Actions running tests | Git workflow, Docker, CI, pytest | week 2 | ☐ |
| M1 | Data model (Event, TicketType, Attendee, CheckIn), migrations, admin, indexes | SQL, schema design, Django | week 4 | ☐ |
| M2 | REST API with auth, permissions, filtering, pagination, OpenAPI docs; 80%+ test coverage | DRF, REST design, TDD | week 6 | ☐ |
| M3 | React frontend: events, registration, check-in screen, dashboard | JS/TS, React | week 8 | ☐ |
| M4 | Logging, `/health`, Docker image, bash backup script, deploy to cloud, deploy workflow, write a post-mortem for a planted failure | Linux, logging, cloud, CI/CD, troubleshooting | week 10 | ☐ |
| M5 | Load test, CSV import/export, architecture diagram, demo, final README, resume bullets | Performance, docs, communication | week 12 | ☐ |

## Working agreement
- The student writes the code. Claude explains, reviews, and unblocks. Every concept gets explained before it's used, because the student must be able to defend each line in an interview.
- Small commits on feature branches and pull requests, even working alone.
- Numbers on the resume come only from real measurements.

## How to run
```bash
# filled in at M0
```

## Results (measured, not guessed)
- Test coverage: 
- Load test (p95 latency at N concurrent users): 
- Records loaded: 

## What I learned / interview talking points
-

## Resume bullets (only after they're true)
-
