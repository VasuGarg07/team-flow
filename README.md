# TeamFlow

TeamFlow is a backend for a team task app, like a small Jira or Trello. People can sign up, log in, make workspaces, add projects, and track tasks with their team.

I am building it in 30 days to learn how real backends work.

## What works today

- Register, log in, refresh the session, and log out
- Passwords are hashed with Argon2 and never stored as plain text
- Short-lived access tokens and a refresh token kept in an HttpOnly cookie
- Create and read users, with one clear JSON shape for every error
- PostgreSQL schema for users, workspaces, members, projects, tasks and comments

## Coming next

- Workspaces with roles (Owner, Admin, Member)
- Projects and tasks, with filters, sorting and pagination
- Comments and file attachments
- Live task updates and background jobs for notifications

## Tech used

- Python, FastAPI and Uvicorn
- PostgreSQL with SQLAlchemy and Alembic migrations
- Pydantic for request and response checks
- JWT (PyJWT) and Argon2 (pwdlib) for authentication
- uv for packages, Docker for the local database

The `frontend` folder (React, TypeScript, Vite) is set up but not used yet.

## How to run it

1. Start PostgreSQL in Docker:
   ```
   docker run --name teamflow-db -e POSTGRES_USER=<user> -e POSTGRES_PASSWORD=<password> -e POSTGRES_DB=<db_name> -p 5432:5432 -v teamflow_pgdata:/var/lib/postgresql/data -d postgres:16
   ```
2. Go into the backend folder:
   ```
   cd backend
   ```
3. Install packages:
   ```
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in the values. Make the secret with:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
5. Create the tables:
   ```
   uv run alembic upgrade head
   ```
6. Start the server:
   ```
   uv run fastapi dev app/main.py
   ```
7. Open http://127.0.0.1:8000/health. You should see `{"status": "ok"}`.

All routes can be tried at http://127.0.0.1:8000/docs.

## Endpoints so far

| Method | Path | What it does | Needs login |
|--------|------|--------------|-------------|
| GET | /health | Says the server is running | No |
| POST | /auth/register | Creates an account | No |
| POST | /auth/login | Returns an access token and sets the refresh cookie | No |
| POST | /auth/refresh | Returns a new access token using the refresh cookie | Cookie |
| DELETE | /auth/logout | Clears the refresh cookie | Cookie |
| GET | /auth/me | Returns the signed-in user | Yes |
| GET | /users/{id} | Returns one user | Yes |

"Yes" means an `Authorization: Bearer <access token>` header.

## Error format

Every error uses the same shape:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  }
}
```

Input mistakes (status 422) also have a `details` list with the field name and a message.

## How login works

1. Login gives an access token (15 minutes) in the response body, and sets a refresh token (7 days) in an HttpOnly cookie.
2. The client sends the access token on every request.
3. When it expires, the client calls `/auth/refresh`. The browser sends the cookie by itself, and the server returns a new access token and a new refresh cookie.
4. Logout clears the cookie.

The cookie is HttpOnly (JavaScript cannot read it), SameSite=strict, limited to the `/auth` path, and Secure in production.

## Refresh token rotation (design note, not built yet)

Right now refresh tokens are stateless JWTs, so logout only removes the cookie. A token copied before logout still works until it expires, and the server cannot cancel it. A safer design would store refresh tokens in a `refresh_tokens` table with a hash of the token, a family id, an expiry time and a revoked time. Every refresh would revoke the old token and issue a new one (rotation). If an old token is used again, someone has a stolen copy, so the whole family is revoked and the user must log in again. Logout, a password change, or "log out everywhere" would revoke the user's tokens.

## Folder layout

All code is in `backend/app`:

- `routers/` - the URLs, and the thin handling of each request
- `services/` - the business rules
- `repositories/` - database queries
- `schemas/` - Pydantic classes for what comes in and what goes out
- `models/` - SQLAlchemy classes, one per database table
- `dependencies.py` - shared checks, like finding the signed-in user
- `security.py` - password hashing and tokens
- `errors.py` and `error_handlers.py` - app errors and the one JSON error format
- `config.py` and `database.py` - settings from `.env` and the database connection
- `../migrations/` - Alembic database migrations