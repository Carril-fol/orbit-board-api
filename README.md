# Orbit Board API

Orbit Board is a project management API designed to eliminate friction in collaboration. Users create projects, grow a team through invitations or join requests, and organise the work as hierarchical tasks with assignees and comments. Every relevant change is recorded in an audit trail.

Built with FastAPI on a fully asynchronous stack: SQLAlchemy 2.0 async and asyncpg over PostgreSQL.

## ✨ Features

*   **Workspace Management**: Control over the creation, configuration, and management of your personal projects.
*   **Open Collaboration System**: Two ways to grow a team — the owner sends invitations, or a user sends a join request the owner approves or declines.
*   **Hierarchical Planning**: Task management with subtask support, allowing complex objectives to be broken down into simpler subtasks. A task's progress is derived from how many of its subtasks are done.
*   **Task Assignment**: The project owner assigns and unassigns collaborators on individual tasks.
*   **Full Traceability**: Every change is stored as a diff between the previous and the new state. Actions that are not field changes — assigning a user, deleting a task — are stored as events with their full payload.
*   **Soft Delete**: Deleted tasks keep their row and stop being returned, so history stays intact.

## 🛠️ Tech Stack

*   **Backend:** Python 3.13, FastAPI, Pydantic v2
*   **Database:** PostgreSQL (Neon Serverless), SQLAlchemy 2.0 async, asyncpg
*   **Migrations:** Alembic
*   **Auth:** JWT in HttpOnly cookies, Argon2 password hashing (`pwdlib`)
*   **Dependency Management:** [uv](https://github.com/astral-sh/uv)
*   **Caching & Rate Limiting:** Redis, `fastapi-cache2`, `slowapi`
*   **Containerization:** Docker (multi-stage build)

## 🏗️ Architecture

The code is organised by **domain module** rather than by technical layer. Each module under `src/` owns its slice end to end:

```
src/<module>/
├── controllers/     HTTP routes; no business rules
├── services/        business rules; the only layer that decides anything
├── repositories/    database access; no business rules
├── interfaces.py    the abstract contract this module exposes to other modules
├── dependencies.py  wiring: builds the service, hands back the interface
├── schemas/         Pydantic input/output
├── models/          SQLAlchemy tables
└── exceptions/      domain errors, translated to HTTP centrally
```

Modules: `auth`, `users`, `projects`, `projects_tags`, `collaborators`, `project_invitations`, `requests`, `tasks`, `comments`, `audit_logs`, plus `shared` and `core`.

## 🚀 Getting Started

Follow this steps to configure the project locally

### Prerequisites

*   Python 3.13 or higher
*   [uv](https://github.com/astral-sh/uv)
*   Git
*   A PostgreSQL database — the project targets [Neon](https://neon.tech), any PostgreSQL works
*   Redis (optional; needed for caching and rate limiting)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/carril-fol/orbit-board-api.git
   cd orbit-board-api
   ```

2. Sync the dependencies with `uv`:
   ```bash
   uv sync
   ```

### Configuration

1. Create a .env file in the project root:
   ```bash
   cp .env.example .env
   ```

2. Configure your environment variables:

| Variable | Required | Description |
|---|---|---|
| `ENV` | no | `development` (default) or `production`. Selects the settings class. |
| `NEON_DATABASE_URL` | **yes** | Connection string, e.g. `postgresql+asyncpg://user:pass@host/db`. Neon's `sslmode` and `channel_binding` parameters are translated for asyncpg automatically. |
| `SECRET_KEY` | **yes** | Key used to sign JWTs. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. |
| `JWT_SECRET_KEY` | **yes** | Required by the settings class, but not read by any code yet — see Known limitations. |
| `REDIS_URL` | no | Redis connection string, for caching and rate limiting. |
| `SERVER_HOST` | no | Defaults to `0.0.0.0`. |
| `SERVER_PORT` | no | Defaults to `8000`. |

3. Apply the migrations:
   ```bash
   uv run alembic upgrade head
   ```

### Running the App

Start the server:
```bash
   py main.py
```
The application will be available at http://localhost:8000. You can access the interactive API documentation at `/docs`.

### Running with Docker

```bash
docker build -t orbit-board-api .
docker run --env-file .env -p 8000:8000 orbit-board-api
```

The image is multi-stage: dependencies are resolved in a builder stage, and only the virtualenv and the application code land in the final image.

### Migrations

```bash
uv run alembic upgrade head                # apply pending migrations
uv run alembic revision -m "description"   # create a new revision
uv run alembic history                     # see the history
```

## 📡 API Overview

All routes are prefixed `/<resource>/api/v1`. Authentication is a JWT cookie, set on login and rotated on refresh.

| Resource | Endpoints |
|---|---|
| **Auth** | `POST /register`, `POST /login`, `POST /logout`, `GET /refresh` |
| **Projects** | `GET /`, `POST /create`, `GET /get/{id}`, `PATCH /update/{id}`, `DELETE /delete/{id}` |
| **Tasks** | `POST /create/{project_id}`, `GET /get/all/{project_id}`, `GET /get/{task_id}`, `GET /get/search/{term}`, `PUT /update/{task_id}`, `DELETE /delete/{task_id}` |
| **Task assignment** | `POST /{task_id}/users`, `DELETE /{task_id}/users/{user_id}` |
| **Collaborators** | `GET /get/{project_id}`, `PUT /update-role/{id}`, `DELETE /delete/{id}` |
| **Invitations** | `POST /create`, `POST /{token}/accept`, `POST /{token}/reject`, `DELETE /remove/{id}` |
| **Join requests** | `POST /create/{project_id}`, `GET /all/{project_id}`, `GET /{request_id}`, `POST /approve/{id}`, `POST /decline/{id}` |
| **Tags** | `POST /create/{project_id}`, `DELETE /delete/{id}` |
| **Comments** | `POST /create/{task_id}`, `GET /get/all/{task_id}`, `GET /get/{id}`, `PUT /update/{id}`, `DELETE /delete/{id}` |

The full contract, with request and response schemas, is at `/docs`.

### Example flow

```bash
# 1. Register, then log in — the session cookie is stored in cookies.txt
curl -X POST localhost:8000/auth/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Ada","last_name":"Lovelace","username":"ada",
       "email":"ada@example.com","password":"a-strong-password",
       "confirm_password":"a-strong-password"}'

curl -X POST localhost:8000/auth/api/v1/login -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"ada@example.com","password":"a-strong-password"}'

# 2. Create a project
curl -X POST localhost:8000/projects/api/v1/create -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"name":"Orbit","description":"Ship the thing","status":"ACTIVE","max_collaborators":5}'

# 3. Add a task to it
curl -X POST localhost:8000/tasks/api/v1/create/1 -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"Design the schema","status":"TO DO","priority":"HIGH"}'

# 4. Read the project's tasks, with their subtasks and progress
curl localhost:8000/tasks/api/v1/get/all/1 -b cookies.txt
```

