# Orbit Board API

[![Live Demo](https://img.shields.io/badge/Live_Demo-API_Docs-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://orbit-board-api.onrender.com/docs)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Carril-fol/orbit-board-api)

Orbit Board is a project management API designed to eliminate friction in collaboration. Users create projects, grow a team through invitations or join requests, and organise the work as hierarchical tasks with assignees and comments.

## 🌐 Try it live

The API is deployed on Render, with an interactive Swagger UI where you can test every endpoint from the browser:

**👉 [orbit-board-api.onrender.com/docs](https://orbit-board-api.onrender.com/docs)**

> [!NOTE]
> The demo runs on a free instance that goes to sleep after a period of inactivity. The first request can take a few seconds to wake it up — after that it responds normally.

**Quick walkthrough:**

1. Open [`/docs`](https://orbit-board-api.onrender.com/docs).
2. Create an account with `POST /auth/api/v1/register`.
3. Log in with `POST /auth/api/v1/login` — the session is kept in a cookie.
4. Create a project with `POST /projects/api/v1/`, then add tasks, invite collaborators or check the audit trail.

Health check: [`/health`](https://orbit-board-api.onrender.com/health)

## ✨ Features

*   **Workspace Management**: Control over the creation and management of your personal projects.
*   **Open Collaboration System**: Two ways to grow a team — the owner sends invitations, or a user sends a join request the owner approves or declines.
*   **Publishing**: You can choose whether a project is `PRIVATE` or `PUBLIC`. If published as `PUBLIC`, the project will appear in the list visible to users; if `PRIVATE`, it will not appear in that list, and users will only be able to join via invitations.
*   **Hierarchical Planning**: Task management with subtask support, allowing complex objectives to be broken down into simpler subtasks. A task's progress is derived from how many of its subtasks are done.
*   **Task Assignment**: The project owner assigns and unassigns collaborators on individual tasks.
*   **Full Traceability**: Every change is stored as a diff between the previous and the new state. Actions like assigning a user, deleting a task — are stored as events with their information.
*   **Soft Delete**: Deleted tasks keep their row and stop being returned, so history stays intact.

## 🛠️ Tech Stack

*   **Backend:** Python 3.13, FastAPI, Pydantic v2
*   **Database:** PostgreSQL (Neon Serverless), SQLAlchemy 2.0 async, asyncpg
*   **Migrations:** Alembic
*   **Containerization:** Docker (multi-stage build)
*   **Deployment:** Render

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
| `ENV` | no | `development`, `production` or `testing`. Selects the settings class. An exported environment variable takes precedence over the value in `.env`. |
| `DATABASE_URL` | **yes** | Connection string, e.g. `postgresql+asyncpg://user:pass@host/db`. |
| `SECRET_KEY` | **yes** | Key used to sign JWTs. |
| `CORS_ORIGINS` | in production | Browser origins allowed to call the API, comma-separated (`https://app.example.com,https://admin.example.com`). Empty means no browser origin is allowed — the API authenticates with cookies, so there is no safe wildcard. Development defaults to `localhost:3000` and `localhost:5173`. |
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

### Deploy to Render

The repository includes a [`render.yaml`](render.yaml) blueprint, so you can deploy your own copy in a few clicks:

1. Click the **Deploy to Render** button at the top of this README.
2. Fill in the values Render asks for: `DATABASE_URL` (a PostgreSQL connection string, e.g. from [Neon](https://neon.tech)) and `CORS_ORIGINS`. `SECRET_KEY` is generated automatically.
3. Once the service is up, apply the migrations against your database:
   ```bash
   DATABASE_URL="postgresql+asyncpg://user:pass@host/db" uv run alembic upgrade head
   ```
4. Open `https://<your-service>.onrender.com/docs`.

### Migrations

```bash
uv run alembic upgrade head                # apply pending migrations
uv run alembic revision -m "description"   # create a new revision
uv run alembic history                     # see the history
```

### Running the Tests

The tests use a PostgreSQL instance in Docker to avoid using the production database.

```bash
docker compose up -d test_db
uv run pytest
```

The container listens on port `5433`, so it never collides with a local PostgreSQL on the default port. `tests/conftest.py` sets `ENV=testing` before the application is imported.

## 📡 API Overview

| Resource | Endpoints |
|---|---|
| **Auth** | `POST /auth/api/v1/register`, `POST /auth/api/v1/login`, `POST /auth/api/v1/logout`, `POST /auth/api/v1/refresh` |
| **Users** | `GET /users/api/v1/me` |
| **Projects** | `POST /projects/api/v1/`, `GET /projects/api/v1/` (the open board), `GET /projects/api/v1/me`, `GET /projects/api/v1/{project_id}`, `PATCH /projects/api/v1/{project_id}`, `DELETE /projects/api/v1/{project_id}` |
| **Tasks** | `POST /projects/api/v1/{project_id}/tasks`, `GET /projects/api/v1/{project_id}/tasks`, `GET /tasks/api/v1/{task_id}`, `PUT /tasks/api/v1/{task_id}`, `DELETE /tasks/api/v1/{task_id}` |
| **Task assignment** | `POST /tasks/api/v1/{task_id}/users`, `DELETE /tasks/api/v1/{task_id}/users/{user_id}` |
| **Comments** | `POST /tasks/api/v1/{task_id}/comments`, `GET /tasks/api/v1/{task_id}/comments`, `GET /comments/api/v1/{comment_id}`, `PUT /comments/api/v1/{comment_id}`, `DELETE /comments/api/v1/{comment_id}` |
| **Collaborators** | `GET /projects/api/v1/{project_id}/collaborators`, `PATCH /collaborators/api/v1/{collaborator_id}`, `DELETE /collaborators/api/v1/{collaborator_id}` |
| **Invitations** | `POST /invitations/api/v1/`, `GET /invitations/api/v1/received`, `POST /invitations/api/v1/{token}/accept`, `POST /invitations/api/v1/{token}/reject`, `DELETE /invitations/api/v1/{invitation_id}` |
| **Join requests** | `POST /projects/api/v1/{project_id}/requests`, `GET /projects/api/v1/{project_id}/requests`, `GET /requests/api/v1/sent`, `GET /requests/api/v1/{request_id}`, `POST /requests/api/v1/{request_id}/approve`, `POST /requests/api/v1/{request_id}/decline` |
| **Tags** | `POST /projects/api/v1/{project_id}/tags`, `DELETE /project-tags/api/v1/{tag_id}` |
| **Audit trail** | `GET /projects/api/v1/{project_id}/audit-logs` |
| **Core** | `GET /health` |

Reading a project depends on its `visibility`. A `PUBLIC` project is listed on the open board (`GET /projects/api/v1/`) and readable by any signed-in user. A `PRIVATE` one is readable only by its owner and collaborators.

### Example flow

Run it locally against `localhost:8000`, or replace that with `https://orbit-board-api.onrender.com` to use the live demo.

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
curl -X POST localhost:8000/projects/api/v1/ -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"name":"Orbit","description":"Ship the thing","status":"ACTIVE","max_collaborators":5,"visibility":"PUBLIC"}'

# 3. Add a task to it
curl -X POST localhost:8000/projects/api/v1/1/tasks -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"Design the schema","status":"TO DO","priority":"HIGH"}'

# 4. Read the project's tasks, with their subtasks and progress
curl localhost:8000/projects/api/v1/1/tasks -b cookies.txt

# 5. See everything that happened in the project
curl localhost:8000/projects/api/v1/1/audit-logs -b cookies.txt
```