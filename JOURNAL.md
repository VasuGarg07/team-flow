### 19 October, 2026 | backend
- Initialised code structure with uv and added fastapi and created health check api

### 20 October, 2026 | backend
- Decision: dropped the Sprint table and the task type column to keep scope small. Rejected keeping them because the 30-day plan does not need them and adding them later is a good migration exercise. WorkspaceMember role now means OWNER / ADMIN / MEMBER (what a person may do), not job titles like QA or DEV. Job title can be a separate column later.
- Ran Postgres 16 in Docker inside WSL and connected to it from FastAPI using SQLAlchemy and psycopg. Settings now come from .env through pydantic-settings.
- Wrote six models (User, Workspace, WorkspaceMember, Project, Task, Comment) and applied the first Alembic migration. Checked the result in psql with \dt and \d tasks.
- What broke: the first connection check hung because the Docker container was not running. Learned to test inside the container first, then from the app. Also password_hash was String(50), which is too short for a real hash, and I had copy-pasted the class name Workspace into four files.
- What I learned: the role belongs in WorkspaceMember because it describes a person in one workspace, not the person everywhere. A migration is a saved instruction file, and alembic_version remembers which one ran last. Python default values do not exist in the database, but server_default values do.

### 21 October, 2026 | backend
- Decision: POST /users stores a fixed placeholder in password_hash and does not accept a password. Rejected storing the password as given (never safe) and hashing now (that is Day 5 and needs a new package). The tradeoff is that these users cannot log in, which is fine because login does not exist until Day 6.
- Built POST /users and GET /users/{id} with the flow router -> service -> repository -> database. Pydantic schemas check the shape of the input (422 on bad data). The service checks the duplicate email (409). The router turns a missing user into 404.
- What broke: I first had a password field in UserCreate that the service ignored, which was misleading, so I removed it.
- What I learned: a DTO (schema) controls what comes in and what goes out, so response_model keeps password_hash from leaking. db.scalar returns one result and db.scalars returns many. Book.title on the class is a SQL column piece, while book.title on an object is the real value. FastAPI finds where each parameter comes from by its name and type, and db goes last only because Python wants parameters with defaults after the others. tags only groups endpoints on the /docs page.