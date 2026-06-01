# NL2SQL Agent

A complete Dockerized natural-language-to-SQL system for oil and gas well data.

## Project overview

This repository contains a fully integrated system with three Docker services:

1. `oracle-db` - Oracle Database Express Edition with schema and seed data.
2. `agent` - Python FastAPI service that uses retrieval-augmented generation (RAG) to translate natural language into Oracle SQL, execute queries, and advise chart recommendations.
3. `frontend` - React + Vite UI for entering questions, viewing generated SQL, browsing results, and rendering charts.

## Architecture

### 1. Docker Compose orchestration

The root `docker-compose.yml` file brings up all services together and connects them on a single Docker network.

- `oracle-db` exposes port `1521`
- `agent` exposes port `8000`
- `frontend` exposes port `3000`

The agent service depends on the Oracle DB service becoming healthy before it starts.

### 2. Database layer

Located in `db/`

- `db/Dockerfile` builds the Oracle XE image.
- `db/init/01_schema.sql` creates the `welldata` user and base schema.
- `db/init/02_views.sql` creates the views the agent may query.
- `db/init/03_seed_data.sql` inserts realistic dummy oil and gas well data.

The Oracle schema is intentionally designed so the agent only queries views, not base tables.

### 3. Agent layer

Located in `agent/`

- `agent/requirements.txt` lists Python dependencies.
- `agent/config.py` loads environment variables and constants.
- `agent/main.py` starts the FastAPI application and builds the RAG vector store on startup.
- `agent/api/` holds the FastAPI routes and request/response models.
- `agent/rag/` builds and queries the ChromaDB vector store from the schema manifest.
- `agent/agent/` contains the NL-to-SQL generator, SQL executor, and chart advisor.

Key behaviors:

- The RAG system indexes structured view metadata from `agent/rag/schema_manifest.py`.
- The Gemini model is used via `langchain-google-genai` to generate SQL and chart suggestions.
- SQL execution is performed against Oracle using SQLAlchemy and the `oracledb` driver.

### 4. Frontend layer

Located in `frontend/`

- `frontend/package.json` defines the React dependencies.
- `frontend/Dockerfile` builds the app and serves it with Nginx.
- `frontend/src/` contains the React application and UI components.
- `frontend/src/styles/globals.css` defines a dark industrial theme.

The UI includes:

- natural language query input
- query history panel
- generated SQL status bar
- paginated results table
- chart rendering powered by Recharts

## Folder structure

```
nl2sql-agent/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── db/
│   ├── Dockerfile
│   └── init/
│       ├── 01_schema.sql
│       ├── 02_views.sql
│       └── 03_seed_data.sql
├── agent/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── schema_manifest.py
│   │   ├── embedder.py
│   │   └── retriever.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── nl2sql.py
│   │   ├── executor.py
│   │   └── chart_advisor.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── models.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── client.ts
        ├── components/
        │   ├── QueryInput.tsx
        │   ├── ResultTable.tsx
        │   ├── ChartPanel.tsx
        │   ├── HistoryPanel.tsx
        │   └── StatusBar.tsx
        └── styles/
            └── globals.css
```

## How it works

1. The frontend sends a plain-English question to the agent API.
2. The agent retrieves schema context from ChromaDB based on the question.
3. Gemini generates a valid Oracle SQL query using only allowed views.
4. The agent executes the SQL query against the Oracle database.
5. The backend returns query results and a chart recommendation.
6. The frontend displays the SQL, result table, and rendered chart.

## Setup and run

### Requirements

- Docker and Docker Compose
- A Google AI Studio API key with Gemini access

### First-time setup

1. Copy the environment template:

```bash
cd c:\Users\LENOVO\Desktop\ongcchatbot\nl2sql-agent
copy .env.example .env
```

2. Open `.env` and set your Gemini API key:

```text
GEMINI_API_KEY=your_google_ai_studio_key_here
ORACLE_PWD=Oracle123
```

3. Build and start everything:

```bash
docker compose up --build
```

4. Wait until Oracle initializes and the agent starts.

5. Open the UI in your browser:

```text
http://localhost:3000
```

### Health checks

- API health: `http://localhost:8000/api/health`
- Views listing: `http://localhost:8000/api/views`

### Stopping

```bash
docker compose down
```

### Reset data

```bash
docker compose down -v
```

## Development notes

### Agent service

If you want to run the agent locally without Docker:

```bash
cd agent
python -m pip install -r requirements.txt
python main.py
```

### Frontend service

If you want to run the frontend locally:

```bash
cd frontend
npm install
npm run dev
```

## Important details

- The Oracle database is seeded with realistic oil and gas well data.
- The agent is restricted to querying predefined views only.
- The RAG vector store is built from `agent/rag/schema_manifest.py`.
- The frontend is designed with a dark industrial theme and includes charting support.

## Repository remote

The repository will be created on GitHub as `nltosql` and pushed with a remote named `origin`.
