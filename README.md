# TeamFlow

TeamFlow is a backend for a team task app, like a small Jira or Trello. People can sign up, make workspaces, add projects, and track tasks with their team.

I am building it in 30 days to learn how real backends work.

## What the API will do

- Sign up, log in, and log out
- Workspaces with roles: Owner, Admin, Member
- Projects and tasks (who does it, how urgent, due date, status)
- Comments and file attachments
- Live task updates
- Background jobs for notifications

Right now only the health check works. The rest comes day by day.

## Tech used

- Python and FastAPI
- Uvicorn (runs the server)
- uv (manages packages)
- PostgreSQL (database, coming on Day 2)

## How to run it

1. Go into the backend folder:
   ```
   cd backend
   ```
2. Install packages:
   ```
   uv sync
   ```
3. Copy `.env.example` to `.env` and fill in the values.
4. Start the server:
   ```
   uv run fastapi dev app/main.py
   ```
5. Open http://127.0.0.1:8000/health. You should see `{"status": "ok"}`.

You can also see all the routes at http://127.0.0.1:8000/docs.
