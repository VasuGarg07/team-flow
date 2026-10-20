### 19 October, 2026 | backend
- Initialised code structure with uv and added fastapi and created health check api

### 20 October, 2026 | backend
- Decision: dropped the Sprint table and the task type column to keep scope small. Rejected keeping them because the 30-day plan does not need them and adding them later is a good migration exercise. WorkspaceMember role now means OWNER / ADMIN / MEMBER (what a person may do), not job titles like QA or DEV. Job title can be a separate column later.
- Ran Postgres 16 in Docker inside WSL and connected to it from FastAPI using SQLAlchemy and psycopg. Settings now come from .env through pydantic-settings.
- Wrote six models (User, Workspace, WorkspaceMember, Project, Task, Comment) and applied the first Alembic migration. Checked the result in psql with \dt and \d tasks.
- What broke: the first connection check hung because the Docker container was not running. Learned to test inside the container first, then from the app. Also password_hash was String(50), which is too short for a real hash, and I had copy-pasted the class name Workspace into four files.
- What I learned: the role belongs in WorkspaceMember because it describes a person in one workspace, not the person everywhere. A migration is a saved instruction file, and alembic_version remembers which one ran last. Python default values do not exist in the database, but server_default values do.