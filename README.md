# CineReserve Backend

A Django REST Framework backend for movie discovery, session browsing, seat reservation, and ticket checkout with Redis-based seat locking, PostgreSQL persistence, JWT authentication, Celery async tasks, and Docker support.

## Features

- User registration and JWT authentication
- List available movies
- List showtimes, optionally filtered by movie
- Seat map per showtime with `available`, `reserved`, and `purchased` states
- Temporary seat reservation using Redis locks with TTL
- Checkout flow that validates the active lock before creating a ticket
- My Tickets endpoint for authenticated users
- Redis caching for high-read endpoints
- Swagger and ReDoc documentation in development
- Celery configuration for asynchronous tasks
- Docker Compose stack with app, PostgreSQL, Redis, Celery worker, and Celery beat
- Pytest-based test suite

## Tech Stack

- Python 3.13
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL
- Redis
- Celery
- Poetry
- Pytest
- Docker / Docker Compose

## Project Structure

```text
core/        # project settings, root urls, celery bootstrap
movies/      # movie catalog
showtimes/   # rooms, seats, showtimes, reservation lock flow
tickets/     # checkout flow and purchased tickets
users/       # custom user model, register/login
```

## Requirements

- Python 3.13
- Poetry
- PostgreSQL
- Redis

Optional for containerized usage:

- Docker
- Docker Compose

## Environment Variables

Start from `.env.example` and create your own `.env`.

### Example for local development

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=cinereserve
POSTGRES_USER=postgres
POSTGRES_PASSWORD=passwd
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
REDIS_CACHE_URL=redis://127.0.0.1:6379/2
SEAT_LOCK_TTL_SECONDS=600

CELERY_BROKER_URL=redis://127.0.0.1:6379/3
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/4

EMAIL_HOST=smtp.mail.com
EMAIL_PORT=587
EMAIL_HOST_USER=user
EMAIL_HOST_PASSWORD=passwd
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=no-reply@cinereserve.com
```

### Example for Docker Compose

When the application runs inside containers, use service names instead of `127.0.0.1`:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=cinereserve
POSTGRES_USER=postgres
POSTGRES_PASSWORD=passwd
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1
REDIS_CACHE_URL=redis://redis:6379/2
SEAT_LOCK_TTL_SECONDS=600

CELERY_BROKER_URL=redis://redis:6379/3
CELERY_RESULT_BACKEND=redis://redis:6379/4

EMAIL_HOST=smtp.mail.com
EMAIL_PORT=587
EMAIL_HOST_USER=user
EMAIL_HOST_PASSWORD=passwd
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=no-reply@cinereserve.com
```

## Local Installation

### 1. Install dependencies

```bash
poetry install
```

### 2. Activate the Poetry shell

```bash
poetry shell
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a superuser

```bash
python manage.py createsuperuser
```

### 5. Start the development server

```bash
python manage.py runserver
```

Or using the predefined task:

```bash
poetry run task run
```

## Running the Full Stack with Docker Compose

### 1. Build and start all services

```bash
docker compose up --build
```

This starts:

- `backend`
- `worker`
- `beat`
- `db`
- `redis`

### 2. Run migrations inside the backend container

```bash
docker compose exec backend python manage.py migrate
```

### 3. Create a superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

### 4. Open the API

- API root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger: [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)
- ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

## API Documentation

Swagger and ReDoc are only available in development mode (`DEBUG=True`).

When `DEBUG=False`, those routes are not registered and return `404`.

## Initial Data Setup

Movies, rooms, seats, and showtimes are managed through Django Admin.

1. Open `/admin/`
2. Create at least:
   - one `Movie`
   - one `Room` with seats
   - one future `Showtime`

## Available Endpoints

### Root

| Method | Endpoint |
|--------|----------|
| GET | `/` |

### Users

| Method | Endpoint |
|--------|----------|
| POST | `/api/users/register/` |
| POST | `/api/users/token/` |
| POST | `/api/users/token/refresh/` |

### Movies

| Method | Endpoint |
|--------|----------|
| GET | `/api/movies/` |

### Showtimes

| Method | Endpoint |
|--------|----------|
| GET | `/api/showtimes/` |
| GET | `/api/showtimes/?movie_id=<id>` |
| GET | `/api/showtimes/<showtime_id>/seat-map/` |
| POST | `/api/showtimes/<showtime_id>/reserve-seat/` |

### Tickets

| Method | Endpoint |
|--------|----------|
| GET | `/api/tickets/my-tickets/` |
| POST | `/api/tickets/checkout/` |

## Authentication

Protected endpoints require a Bearer JWT token.

```http
Authorization: Bearer <access_token>
```

## Seat Reservation Architecture

The reservation flow is split into two stages:

1. **Reserve** — temporarily locks the seat in Redis with a TTL
2. **Checkout** — validates the active lock and creates a permanent ticket in PostgreSQL

Seat lock expiration is handled natively by Redis TTL. When the TTL expires, the seat is automatically released without any background job. Celery is used for asynchronous side effects such as sending ticket confirmation emails.

## End-to-End Manual Test Flow

### Step 1 — Register a user

`POST /api/users/register/`

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "StrongPassword123"
}
```

### Step 2 — Login and get tokens

`POST /api/users/token/`

```json
{
  "username": "alice",
  "password": "StrongPassword123"
}
```

Response:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

### Step 3 — List available movies

`GET /api/movies/`

### Step 4 — List showtimes for a movie

`GET /api/showtimes/?movie_id=1`

### Step 5 — View the seat map

`GET /api/showtimes/1/seat-map/`

Header (optional for `is_locked_by_me` info):

```http
Authorization: Bearer <access_token>
```

Each seat returns:

```json
{
  "seat_id": 2,
  "row": "A",
  "number": 2,
  "status": "available",
  "is_locked_by_me": false,
  "lock_ttl_seconds": null
}
```

Possible status values: `available`, `reserved`, `purchased`.

### Step 6 — Reserve a seat

`POST /api/showtimes/1/reserve-seat/`

```http
Authorization: Bearer <access_token>
```

```json
{
  "seat_id": 2
}
```

Success response:

```json
{
  "detail": "Seat reserved successfully.",
  "showtime_id": 1,
  "seat_id": 2,
  "lock_ttl_seconds": 600
}
```

### Step 7 — Try reserving the same seat with another user

Register and log in as a second user, then call the same endpoint.

Expected response:

```json
{
  "detail": "This seat is temporarily reserved.",
  "locked_by_me": false,
  "lock_ttl_seconds": 598
}
```

This validates that the Redis lock is working correctly.

### Step 8 — Checkout

`POST /api/tickets/checkout/`

```http
Authorization: Bearer <access_token>
```

```json
{
  "showtime_id": 1,
  "seat_id": 2
}
```

Expected: `201 Created` with the created ticket.

Only the user who holds the active lock can complete checkout.

### Step 9 — List purchased tickets

`GET /api/tickets/my-tickets/`

```http
Authorization: Bearer <access_token>
```

### Step 10 — Verify the seat map

`GET /api/showtimes/1/seat-map/`

The reserved seat should now appear as `purchased`.

## Concurrency Test

1. Create two users and log in with both
2. Reserve the same seat with user 1
3. Try to reserve the same seat with user 2 immediately after
4. Only user 1 succeeds; user 2 receives `409 Conflict`
5. Only user 1 can complete checkout for that seat

## Testing

### Run the full test suite

```bash
poetry run task test
```

### Run with coverage report

```bash
poetry run task test_cov
```

The HTML report is written to `htmlcov/index.html`.

### Run tests by app

```bash
poetry run task test_users
poetry run task test_movies
poetry run task test_showtimes
poetry run task test_tickets
```

## Linting and Formatting

### Check lint

```bash
poetry run task lint
```

### Auto-fix and format

```bash
poetry run task format
```

## Celery

Celery is configured for asynchronous tasks such as sending ticket confirmation emails after a successful checkout.

### Start a worker manually

```bash
poetry run celery -A core worker -l info
```

### Start beat manually

```bash
poetry run celery -A core beat -l info
```

When running via Docker Compose, both `worker` and `beat` services are already included.

## Email Behavior

### Development

When `DEBUG=True`, Django uses the console email backend. Emails are printed to logs and not sent to a real mailbox.

### Production

When `DEBUG=False`, Django uses the SMTP configuration defined in the environment variables.

## Useful Commands

### Local

```bash
poetry install
poetry shell
task migrate
task superuser
task run
task test
task test_cov
task lint
task format
```

### Docker

```bash
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```
