# Orbit Board API

Orbit Board is a project management API designed to eliminate friction in collaboration. It allows users to create workspaces, publish them to attract collaborators or invite specific individuals, and manage workflows through a system of hierarchical tasks and comments.

## ✨ Features

*   **Workspace Management**: Control over the creation, configuration, and management of your personal projects.
*   **Open Collaboration System**: Flexible flow of invitations and requests to join in projects, this allows to coordinate work teams efficient.
*   **Hierarchical Planning**: Task management with subtask support, allowing complex objectives to be broken down into simpler subtasks for more precise progress tracking.
*   **Full Traceability**: System for logging all relevant changes to the entities.
*   **Optimized Performance**: Implementation of caching and rate limiting to secure an answer fast and protect the api from abuse

## 🛠️ Tech Stack

*   **Backend:** Python 3.13, FastAPI
*   **Dependency Management:** [uv](https://github.com/astral-sh/uv) 
*   **Database:** PostgreSQL (Neon Serverless)
*   **Caching & Rate Limiting:** Redis
*   **Hosting:** Render

## 🚀 Getting Started

Follow this steps to configure the project locally

### Prerequisites

*   Python 3.13 or higher 
*   [uv](https://github.com/astral-sh/uv)
*   Git

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
   ```env
    ENV=
    NEON_DATABASE_URL = 
    SECRET_KEY = 
    JWT_SECRET_KEY = 
    SERVER_HOST = 
    SERVER_PORT = 
    REDIS_URL =
   ```

### Running the App

Start the server:
```bash
uv run uvicorn main:app --reload
```
The application will be available at http://localhost:8000. You can access the interactive API documentation at `/docs`.

## Technical decisions

This project was developed following principles focused on maintainability:

*   **Layered Architecture**: Implementation of a layered pattern (Controller → Service → Repository), decoupling business logic from data persistence.
*   **Audit Log System**: Design of an audit service that captures the "diff" between the previous and new state of objects, allowing the history of any entity to be reconstructed.
*   **Global Exception Handling**: Centralized error handling through custom FastAPI handlers, eliminating redundant try-except blocks across services.