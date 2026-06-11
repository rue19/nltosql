# NL2SQL Agent

> Natural-language-to-SQL agent for oil & gas well data, powered by Gemini or local Qwen 0.5B GGUF, with ChromaDB RAG and a React dashboard.

## Quick Start

```bash
cp .env.example .env      # edit GEMINI_API_KEY (or skip for local-only mode)
docker compose up --build  # starts Oracle XE + agent + frontend
```

Open **http://localhost:3000** — agent health at **http://localhost:8000/api/health**.

## Features

| Feature | Description |
|---------|-------------|
| **Natural Language → SQL** | Ask questions in plain English; get executable Oracle SQL. |
| **Local LLM (offline)** | Qwen 2.5 0.5B GGUF via `llama-cpp-python` — no API key required. |
| **Gemini API (primary)** | Google Gemini 1.5 Flash for higher accuracy SQL generation. |
| **Retrieval-Augmented Gen (RAG)** | ChromaDB + ONNX embeddings index 7 view definitions; top-3 relevant views retrieved per question. |
| **SQL Execution** | Queries run against **Oracle XE** inside the same Docker network. |
| **7 Database Views** | Well header, petrophysics, monthly production, formation tops, well summary, core analysis, gas composition. |
| **Chart Advisor** | AI suggests the best chart type (bar, line, scatter, pie, etc.) per query. |
| **Interactive Charts** | Recharts-powered with 7 chart types — switch freely via toggle buttons. |
| **Export** | CSV (table), PNG and SVG (charts). |
| **Table / Chart / Both** | View toggle tabs to switch between result views. |
| **Query History** | Session-based history panel with re-run and delete. |
| **Dark Industrial Theme** | Tailored UI for oil & gas domain. |
| **Docker Compose** | Single command to spin up the full stack. |

## LLM Options

| LLM | Config | Pros | Cons |
|-----|--------|------|------|
| **Gemini 1.5 Flash** (default) | Set `GEMINI_API_KEY` in `.env` | Higher accuracy, structured JSON chart advice, fast | Requires internet & free API quota (60 req/min) |
| **Local Qwen 2.5 0.5B** | Set `USE_LOCAL_LLM=true` + download model | Fully offline, zero cost, no API key | Lower accuracy on complex queries (~491 MB RAM) |

To use the local model:

```bash
# 1. Download the 0.5B Q4_K_M GGUF file
mkdir -p models
wget -O models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf

# 2. Set USE_LOCAL_LLM=true in .env
echo "USE_LOCAL_LLM=true" >> .env

# 3. Rebuild and start
docker compose up --build -d
```

> **Performance note**: The 0.5B Qwen model handles simple single-table `SELECT`/`WHERE` queries well but struggles with multi-view joins, `GROUP BY` aggregation, and precise literal matching. The Gemini model is recommended for production use.

## RAG System

The agent uses **Retrieval-Augmented Generation** to select the most relevant database views for each question:

1. **7 view documents** are stored in `agent/rag/schema_manifest.py` with detailed column descriptions and use-case tags.
2. On startup, **ChromaDB** indexes them using ONNX-based `all-MiniLM-L6-v2` embeddings (79 MB, no PyTorch).
3. At query time, the **retriever** fetches the top-3 most semantically similar views.
4. If no view scores above the confidence threshold (0.3), it falls back to a minimal schema listing all views.
5. Primary key join rules (UWI/UBHI) are **always** injected.

This avoids flooding the LLM with irrelevant schema context and dramatically improves SQL quality.

## Architecture

```
┌──────────────┐     ┌─────────────────────────────────────────────┐
│   Browser    │     │               Docker Network                 │
│  localhost:3000 │     │                                             │
└──────┬───────┘     │  ┌──────────┐    ┌──────────────────────┐    │
       │ HTTP        │  │  Agent   │    │     Oracle XE         │    │
       │             │  │ :8000    │◄──►│     :1521             │    │
       ▼             │  │          │    │  welldata schema      │    │
┌──────────────┐     │  │ ┌──────┐ │    │  7 views              │    │
│  React App   │     │  │ │RAG   │ │    └──────────────────────┘    │
│  (Vite+Nginx)│──┬──►  │ │Chroma│ │                               │
│  - QueryInput│  │   │  │ │DB    │ │                               │
│  - ResultTbl │  │   │  └──────┘ │                               │
│  - ChartPanel│  │   │  ┌────────┴─┐                             │
│  - History   │  │   │  │ LLM      │                             │
└──────────────┘  │   │  │ Gemini   │──► Google AI API             │
                  │   │  │  OR      │                              │
                  │   │  │ Qwen 0.5B│──► local GGUF (offline)      │
                  │   │  └──────────┘                              │
                  │   └─────────────────────────────────────────────┘
```

## Project Structure

```
nltosql/
├── docker-compose.yml       # Orchestrates all 3 services
├── .env.example             # Environment variable template
├── .gitignore
├── README.md
├── db/
│   ├── Dockerfile           # Oracle XE 21.3.0 image
│   └── init/
│       ├── 01_schema.sql    # welldata user + base tables
│       ├── 02_views.sql     # 7 analysis views
│       └── 03_seed_data.sql # Realistic Indian basin well data
├── agent/
│   ├── Dockerfile           # Python 3.11 + dependencies
│   ├── requirements.txt
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic settings (env-based)
│   ├── api/
│   │   ├── routes.py        # /query, /health, /views endpoints
│   │   └── models.py        # Pydantic request/response schemas
│   ├── agent/
│   │   ├── nl2sql.py        # NL → SQL generation
│   │   ├── executor.py      # SQL execution against Oracle
│   │   └── chart_advisor.py # Chart type recommendation
│   └── rag/
│       ├── schema_manifest.py # View definitions + PRIMARY KEY rules
│       ├── embedder.py       # ChromaDB vector store builder
│       └── retriever.py      # Semantic view retrieval
└── frontend/
    ├── Dockerfile           # Node → Nginx multi-stage build
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx           # Root component with view toggle
        ├── api/client.ts     # Backend API client
        ├── components/
        │   ├── QueryInput.tsx    # Natural language input
        │   ├── ResultTable.tsx   # Paginated results + CSV download
        │   ├── ChartPanel.tsx    # 7 chart types + PNG/SVG export
        │   ├── HistoryPanel.tsx  # Query history sidebar
        │   └── StatusBar.tsx     # SQL + row count display
        └── styles/globals.css   # Dark industrial theme
```

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | No* | `""` | Google AI Studio API key |
| `ORACLE_PWD` | No | `Oracle123` | Oracle SYS + welldata password |
| `USE_LOCAL_LLM` | No | `false` | Set to `true` to use Qwen GGUF instead of Gemini |
| `QWEN_MODEL_PATH` | No | `/app/models/qwen2.5-0.5b-instruct-q4_k_m.gguf` | Path to GGUF file inside container |
| `QWEN_CONTEXT_LENGTH` | No | `4096` | Context window for local LLM |
| `QWEN_MAX_TOKENS` | No | `512` | Max output tokens |
| `QWEN_TEMPERATURE` | No | `0.0` | LLM temperature |
| `MAX_ROWS` | No | `500` | Max rows returned per query |

\* `GEMINI_API_KEY` is only required when `USE_LOCAL_LLM=false` (the default). When using local Qwen, it can be left blank.

## API Reference

### `POST /api/query`

Submit a natural language question.

**Request:**
```json
{ "question": "Which wells produced the most oil in 2024?" }
```

**Response:**
```json
{
  "question": "Which wells produced the most oil in 2024?",
  "sql": "SELECT WELL_NAME, SUM(OIL_BBL) FROM welldata.V_PRODUCTION_MONTHLY WHERE PROD_YEAR = 2024 GROUP BY WELL_NAME ORDER BY SUM(OIL_BBL) DESC FETCH FIRST 10 ROWS ONLY",
  "columns": ["WELL_NAME", "SUM(OIL_BBL)"],
  "rows": [["WELL-001", 125000], ["WELL-042", 98000]],
  "row_count": 10,
  "chart_advice": {
    "chart_type": "bar",
    "x_column": "WELL_NAME",
    "y_column": "SUM(OIL_BBL)",
    "title": "Top 10 Wells by Oil Production (2024)",
    "reason": "Bar chart compares categorical well names against a numeric production value."
  }
}
```

### `GET /api/health`

```json
{ "status": "ok", "db_connected": true, "rag_ready": true }
```

### `GET /api/views`

Returns the list of 7 available database views with descriptions.

## Database Views

| View | Description |
|------|-------------|
| `welldata.V_WELL_HEADER` | Well identity, location, operator, basin, dates, depth, status |
| `welldata.V_PETROPHYSICS` | Reservoir quality (porosity, permeability, saturation) per borehole |
| `welldata.V_PRODUCTION_MONTHLY` | Monthly oil, gas, water production per well |
| `welldata.V_FORMATION_TOPS` | Stratigraphic formation tops per well |
| `welldata.V_WELL_SUMMARY` | Aggregated lifetime stats per well |
| `welldata.V_CORE_ANALYSIS` | Lab core analysis per well |
| `welldata.V_GAS_COMPOSITION` | Natural gas compositional analysis per well |

## Example Queries

**Well identity & location:**
- "Show me all wells in the Krishna-Godavari basin"
- "List active exploration wells drilled after 2020"
- "Which operator has the most wells in the Cambay basin?"

**Production:**
- "Top 10 wells by cumulative oil production"
- "Monthly gas production trend for WELL-001 in 2024"
- "Which field produced the most oil in 2023?"

**Reservoir & petrophysics:**
- "Wells with porosity above 0.2 in the Kamalapuram formation"
- "Average permeability by formation"
- "Horizontal wells with excellent reservoir quality"

**Formations & geology:**
- "Thickness of the Basal Sandstone formation across all wells"
- "Wells where the Kamalapuram formation is deeper than 3000 meters"
- "Formations with sandstone lithology in the Krishna-Godavari basin"

**Gas composition:**
- "Wells with sour gas (H2S above 0.5%)"
- "Average methane percentage by basin"
- "Rich gas wells in the KG basin"

**Cross-view joins:**
- "Show well name, operator, cumulative oil, and average porosity for each well"
- "List wells with both high permeability and high gas production"

## Frontend Features

### View Toggle
Switch between **Table**, **Chart**, or **Both** views using the toggle bar above results. Both views show by default.

### Chart Types
| Chart | Icon | Use Case |
|-------|------|----------|
| Bar | ▬ | Categorical comparison |
| Horizontal Bar | ▮ | Long category labels |
| Line | 〜 | Time series / trends |
| Area | ◿ | Cumulative or volume trends |
| Scatter | ⁙ | Correlation between two numeric variables |
| Histogram | ▦ | Distribution of a single numeric column |
| Pie | ◔ | Part-of-whole proportions |

### Export
- **CSV**: Download table data from the ResultTable component.
- **PNG**: Download current chart as a PNG image.
- **SVG**: Download current chart as a scalable vector graphic.

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `db_connected: false` | Oracle still initializing | Wait 2–3 min; check `docker logs oracle-db` |
| Agent won't start | Oracle not healthy yet | `docker compose up` waits automatically |
| Empty results | Query returned no matches | Try simpler question; check view columns |
| `llama-cpp-python` import error | Wrong architecture (x86 vs ARM) | Use `LLAMA_CPU_AARCH64=1` on ARM or `CMAKE_ARGS="-DLLAMA_METAL=on"` on macOS |
| Gemini quota error | Free tier rate limit (60 req/min) | Agent retries with backoff (up to 4 attempts) |
| ChromaDB telemetry error | ChromaDB version mismatch | Cosmetic only — no impact on functionality |
| Port conflict | Something already on 1521/8000/3000 | Change ports in `docker-compose.yml` |
| Charts show "none" | Local 0.5B model can't generate JSON reliably | Use Gemini for chart advice or expect `chart_type: "none"` fallback |

## Deployment (Oracle Cloud Free Tier)

The full stack runs comfortably on an **Oracle Cloud Free Tier ARM instance** (VM.Standard.A1.Flex, 4 OCPU, 24 GB RAM). Oracle XE itself uses the A1 instance's built-in Oracle DB compatibility.

### Steps

1. **Provision** an ARM instance with Ubuntu 22.04 + 100 GB boot volume.
2. **Open ports** 22, 3000, 8000 in the VCN security list.
3. **SSH in** and install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker ubuntu
   ```
4. **Clone and build:**
   ```bash
   git clone https://github.com/rue19/nltosql.git
   cd nltosql
   cp .env.example .env
   # edit .env with your settings
   docker compose up --build -d
   ```
5. **Verify:**
   ```bash
   curl http://localhost:8000/api/health
   ```
6. **(Optional)** Set up **Cloudflare Tunnel** for free HTTPS without opening firewall ports.

## Development

### Run agent locally (no Docker)

```bash
cd agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Ensure Oracle XE is accessible (host machine or Docker)
python main.py
```

### Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

The dev server proxies API requests to `http://localhost:8000` per the `VITE_API_URL` env var.

## License

MIT
