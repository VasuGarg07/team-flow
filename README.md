# TeamFlow

TeamFlow is a backend for a team task app, like a small Jira or Trello. People can sign up, log in, make workspaces, add projects, and track tasks with their team.

I am building it in 30 days to learn how real backends work.

## What works today

- Register, log in, refresh the session, and log out
- Passwords are hashed with Argon2 and never stored as plain text
- Short-lived access tokens and a refresh token kept in an HttpOnly cookie
- Workspaces with three roles (Owner, Admin, Member) and member management
- Projects and tasks inside workspaces, protected so one workspace can never read another's data
- Task lists with filters, sorting and pages
- Names and roles in the answers, so a screen needs no extra requests
- One clear JSON shape for every error
- PostgreSQL schema for users, workspaces, members, projects, tasks and comments
- A seed script that fills the local database with realistic demo data
- An index for the task list query, checked with EXPLAIN ANALYZE
- Removing a member un-assigns their tasks in the same transaction
- The project list is cached in Redis and cleared when projects change
- Login and register are rate limited per IP, with a Retry-After header
- Assigning a task queues a notification job that a separate worker runs

## Coming next

- Comments, file attachments and live task updates
- Docker Compose, automated tests, CI and deployment

## Tech used

- Python, FastAPI and Uvicorn
- PostgreSQL with SQLAlchemy and Alembic migrations
- Pydantic for request and response checks
- JWT (PyJWT) and Argon2 (pwdlib) for authentication
- Redis for the cache, the rate limiter and the job queue, and RQ for background jobs
- uv for packages, Docker for the local database and Redis
- React, TypeScript, Vite and Tailwind for the frontend

The `frontend` folder holds a React app that uses this API.

## How to run it

1. Start PostgreSQL in Docker:
   ```
   docker run --name teamflow-db -e POSTGRES_USER=<user> -e POSTGRES_PASSWORD=<password> -e POSTGRES_DB=<db_name> -p 5432:5432 -v teamflow_pgdata:/var/lib/postgresql/data -d postgres:16
   ```
   Start Redis in Docker too:
   ```
   docker run --name teamflow-redis -p 6379:6379 -d redis:7
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
6. Optional: fill the database with demo data (this deletes everything in the local database first):
   ```
   uv run python -m scripts.seed --yes
   ```
7. Start the server:
   ```
   uv run fastapi dev app/main.py
   ```
8. Open http://127.0.0.1:8000/health. You should see `{"status": "ok"}`.
9. To run background jobs, start the worker in a Linux shell (WSL) in a second terminal. It does not run on plain Windows:
   ```
   uv run rq worker default
   ```

All routes can be tried at http://127.0.0.1:8000/docs.

To run the frontend, start the backend first, then in a second terminal:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The dev server forwards the API calls to the backend on port 8000, so no CORS setup is needed.

## Endpoints so far

| Method | Path | What it does | Who can use it |
|--------|------|--------------|----------------|
| GET | /health | Says the server is running | Anyone |
| POST | /auth/register | Creates an account | Anyone |
| POST | /auth/login | Returns an access token and sets the refresh cookie | Anyone |
| POST | /auth/refresh | Returns a new access token using the refresh cookie | Refresh cookie |
| DELETE | /auth/logout | Clears the refresh cookie | Refresh cookie |
| GET | /auth/me | Returns the signed-in user | Logged in |
| GET | /users/{id} | Returns one user | Logged in |
| POST | /workspaces | Creates a workspace, and you become its owner | Logged in |
| GET | /workspaces | Lists the workspaces you belong to, each with your role | Logged in |
| GET | /workspaces/{workspace_id} | Returns one workspace with your role | Any member |
| PATCH | /workspaces/{workspace_id} | Renames the workspace | Owner, Admin |
| DELETE | /workspaces/{workspace_id} | Deletes the workspace and everything inside it | Owner |
| GET | /workspaces/{workspace_id}/members | Lists the members with their user details | Any member |
| POST | /workspaces/{workspace_id}/members | Adds a member by email | Owner, Admin |
| PATCH | /workspaces/{workspace_id}/members/{target_user_id} | Changes a member's role | Owner |
| DELETE | /workspaces/{workspace_id}/members/{target_user_id} | Removes a member | Owner, Admin |
| GET | /workspaces/{workspace_id}/projects | Lists the workspace's projects | Any member |
| GET | /workspaces/{workspace_id}/projects/{project_id} | Returns one project | Any member |
| POST | /workspaces/{workspace_id}/projects | Creates a project | Owner, Admin |
| PATCH | /workspaces/{workspace_id}/projects/{project_id} | Updates a project (only the fields you send) | Owner, Admin |
| DELETE | /workspaces/{workspace_id}/projects/{project_id} | Deletes a project and its tasks | Owner, Admin |
| GET | /workspaces/{workspace_id}/projects/{project_id}/tasks | Lists the project's tasks, with filters, sorting and pages | Any member |
| GET | /workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id} | Returns one task | Any member |
| POST | /workspaces/{workspace_id}/projects/{project_id}/tasks | Creates a task, and you become its reporter | Any member |
| PATCH | /workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id} | Updates a task (only the fields you send) | Owner, Admin, reporter or assignee |
| DELETE | /workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id} | Deletes a task | Owner, Admin or reporter |

"Logged in" means an `Authorization: Bearer <access token>` header.

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

## Roles and permissions

A role belongs to one person in one workspace. Someone can be the owner of one workspace and a plain member of another.

| Action | Owner | Admin | Member |
|---|---|---|---|
| See the workspace, its members, projects and tasks | Yes | Yes | Yes |
| Rename the workspace | Yes | Yes | No |
| Delete the workspace | Yes | No | No |
| Add a member | Yes | Yes | No |
| Add an admin, or change a role | Yes | No | No |
| Remove a member | Yes | Yes | No |
| Remove an admin | Yes | No | No |
| Create, update or delete projects | Yes | Yes | No |
| Create a task | Yes | Yes | Yes |
| Update a task | Any task | Any task | Only tasks they reported or are assigned to |
| Delete a task | Any task | Any task | Only tasks they reported |

Rules behind the table:

- A workspace has exactly one owner, set when it is created. The owner cannot be removed or demoted, and nobody else can be made an owner.
- Admins can add and remove plain members only.
- A task's reporter is always the person who created it, taken from the token. Its assignee must be a member of the same workspace.
- Roles are looked up from the database on every request, not stored in the token, because they are per workspace and can change.

## How data is kept separate

- A person who is not a member of a workspace gets 404 for it, the same answer as for a workspace that does not exist, so ids cannot be probed.
- Projects and tasks are looked up through their parents: the project by workspace id and project id, and the task by project id and task id. An id from another workspace or project returns 404 (this prevents broken object level authorization).
- The current user always comes from the token, never from the request body.

## Listing tasks: filters, sorting and pages

`GET /workspaces/{workspace_id}/projects/{project_id}/tasks` accepts these query parameters:

| Parameter | Values | Default |
|---|---|---|
| `status` | OPEN, IN_PROGRESS, TESTING, LIVE, VOID | all |
| `priority` | LIVE_ISSUE, BLOCKER, HIGH, MEDIUM, LOW | all |
| `assignee_id` | a user id | all |
| `sort_by` | created_at, due_date, priority, status, story_points, name | created_at |
| `order` | asc, desc | desc |
| `page` | 1 or more | 1 |
| `limit` | 1 to 100 | 20 |

The answer looks like this:

```json
{
  "items": [],
  "total": 200,
  "page": 1,
  "limit": 20
}
```

Notes:

- `sort_by` only accepts the names in the table, so a client can never choose a column freely.
- Every sort ends with the task id, so two pages never repeat or skip a task, and tasks with no value (like a missing due date) always come last.
- This uses offset pagination. For very long feeds a cursor would be faster on deep pages.
- The people on each task are loaded in the same query (a join), so the number of queries does not grow with the page size.

## Redis: cache, rate limit and jobs

Redis is used for three things. If Redis is down the app still works, only slower and without limits.

- **Cache:** `GET /workspaces/{workspace_id}/projects` is saved under `workspace:{id}:projects` for 60 seconds. Creating, updating or deleting a project, or deleting the workspace, deletes that key after the database commit. The role check always runs before the cache.
- **Rate limit:** `POST /auth/login` and `POST /auth/register` allow 5 requests per 60 seconds per IP. Over the limit the answer is 429 with a `Retry-After` header. It is a fixed window counter, so a burst at the window edge is possible, and if Redis is down the request is allowed.
- **Background jobs:** when a task is created with an assignee, or updated to a different assignee (not yourself), a job `send_assignment_notification` is queued after the commit. A worker runs it with up to 3 retries. It only logs a line for now. The job gets the task id and opens its own database session.

## Demo data

The seed script deletes everything in the local database and creates twelve people, three workspaces, nine projects, about eighty five tasks and some comments. Add `--bulk` for five thousand extra tasks in one project.

```
uv run python -m scripts.seed --yes
uv run python -m scripts.seed --yes --bulk
```

Every demo user has the password `password123`.

| Email | Role |
|---|---|
| aarav.mehta@teamflow.example | Owner of Northwind Studio and Weekend Hacks, member of Bright Labs |
| priya.nair@teamflow.example | Admin of Northwind Studio, member of Bright Labs |
| rohan.verma@teamflow.example | Member of Northwind Studio |
| meera.krishnan@teamflow.example | Owner of Bright Labs |
| arjun.singh@teamflow.example | Admin of Bright Labs |

The script refuses to run unless `--yes` is given and the database is on localhost.

## How login works

1. Login gives an access token (15 minutes) in the response body, and sets a refresh token (7 days) in an HttpOnly cookie.
2. The client sends the access token on every request.
3. When it expires, the client calls `/auth/refresh`. The browser sends the cookie by itself, and the server returns a new access token and a new refresh cookie.
4. Logout clears the cookie.

The cookie is HttpOnly (JavaScript cannot read it), SameSite=strict, limited to the `/auth` path, and Secure in production.

## Refresh token rotation (design note, not built yet)

Right now refresh tokens are stateless JWTs, so logout only removes the cookie. A token copied before logout still works until it expires, and the server cannot cancel it. A safer design would store refresh tokens in a `refresh_tokens` table with a hash of the token, a family id, an expiry time and a revoked time. Every refresh would revoke the old token and issue a new one (rotation). If an old token is used again, someone has a stolen copy, so the whole family is revoked and the user must log in again. Logout, a password change, or "log out everywhere" would revoke the user's tokens.

## How a request flows

1. The **router** matches the URL, reads the input (checked by a Pydantic schema), and runs the checks it depends on, like the signed-in user and the workspace role.
2. The **service** applies the business rules and raises an app error when a rule is broken.
3. The **repository** is the only place that talks to the database.
4. The **error handlers** turn any app error into the one JSON error format.

## Folder layout

```
backend/
  app/
    routers/        the URLs, and the thin handling of each request
    services/       the business rules
    repositories/   database queries
    schemas/        Pydantic classes for what comes in and what goes out
    models/         SQLAlchemy classes, one per database table
    dependencies.py shared checks, like the signed-in user and the workspace role
    security.py     password hashing and tokens
    errors.py       app errors
    error_handlers.py  the one JSON error format
    config.py       settings from .env
    database.py     the database connection
    cache.py        Redis cache and rate limit counter
    queue.py        the job queue
    jobs.py         the background jobs the worker runs
  migrations/       Alembic database migrations
  scripts/seed.py   fills the local database with demo data
frontend/           React, TypeScript and Vite app
```
