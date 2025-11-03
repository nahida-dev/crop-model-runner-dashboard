# 🌾 Model Runner Dashboard

An end-to-end **Model Runner Dashboard** prototype for internal decision intelligence workflows.
Users can select a model, submit parameters, trigger a run, watch progress in real-time, and view results — all in a lightweight, full-stack environment.

This project demonstrates how scientific models, data, and decision workflows can be integrated into a cohesive application system.

## 🚀 Overview

### Tech Stack
| Layer | Technology | Description |
|-------|-------------|-------------|
| **Frontend** | React + TypeScript + Vite + Material UI | Interactive dashboard for model selection, run control, and visualization |
| **Backend** | FastAPI (Python) + SQLModel + SQLite | Async API for model execution, persistence, and result delivery |
| **Database** | SQLite (local lightweight store) | Stores models, runs, and results |
| **CI/CD** | GitHub Actions | Automated testing and build for frontend and backend |
| **Auth** | Mock header-based (MSAL-ready) | Simulates internal user authentication and access control |
| **Data** | USDA public dataset + synthetic dataset | Crop yield (real public data) and environmental risk simulation |

## 🧩 Features

### Frontend
- Model selection (e.g., **Crop Yield Predictor**, **Water Risk Model**)
- Run configuration (region, year)
- Trigger run and watch progress live
- Results view with summary metrics and tabular output
- Real-time error handling and loading states
- Mock user authentication (switch users to test access control)

### Backend
- REST API endpoints:
  - `GET /api/models` → list available models
  - `POST /api/runs` → submit a run
  - `GET /api/runs/{id}/status` → get run status
  - `GET /api/runs/{id}/results` → fetch run results
  - `GET /api/regions` → list available regions from the dataset
  - `GET /api/runs` → get get list of runs executed by a particular user
- Async model execution simulation
- Persistence using SQLModel + SQLite
- Lightweight authentication and row-level access control

## 🧪 How to Run Locally (Using VS Code)

### 1️⃣ Backend
```bash
# Open VS Code terminal and navigate to backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Activate it 
.\backend\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# navigate to the project root "model-runner"
cd ..

# Run FastAPI server
uvicorn main:app --reload
```
➡️ Runs at: http://localhost:8000

➡️ API Docs: http://localhost:8000/docs

### 2️⃣ Frontend
```bash
cd frontend
npm install
npm run dev
```
➡️ Open: http://localhost:5173

The frontend automatically proxies API calls to the backend.

## 🧩 Supporting Data Scripts (under /backend/scripts)

Two helper scripts are provided to prepare and refresh datasets used by the models.

### 1️⃣ fetch_usda_yield.py

#### Purpose: 
Fetches real USDA yield data from the [USDA QuickStats API](https://quickstats.nass.usda.gov/).

#### Output: 
Saves a cleaned dataset to:
```bash
/backend/data/yield_data.csv
```
 
#### Usage: 
```bash
python backend/scripts/fetch_usda_yield.py
```

This script uses your USDA API key to retrieve actual yield data (e.g., corn yield in bushels/acre) for multiple Midwest states and years.

### 2️⃣ generate_water_risk_data.py

#### Purpose: 
Generates a synthetic water risk dataset by extending the USDA yield data with irrigation cost and drought index parameters.
#### Input:
```bash
/backend/data/yield_data.csv
```
#### Output: 
Saves a synthetic dataset to:
```bash
/backend/data/water_risk_data.csv
```
#### Usage:
```bash
python backend/scripts/generate_water_risk_data.py
```

This synthetic dataset is used by the Water Risk Model for demonstration and visualization.

## 🔐 Authentication & Authorization

### MVP (Implemented)
- Simulated user login using a dropdown (`UserSelector` component)
- The selected user (e.g., `analyst@corteva.internal`) is stored in `localStorage`
- All API requests include this as a header:
  `x-user-id: <user-email>`
- Backend enforces:
  - Rejects requests without valid `x-user-id` (401 Unauthorized)
  - Associates each run with a `user_id`
  - Only that user can access their runs and results (403 Forbidden if not)

### Production Plan (Design)
- Replace mock header with Microsoft Authentication Library (MSAL) for Azure AD login
- Backend validates tokens (issuer, audience, expiry, signature)
- Use AAD user object ID (`oid`) as `user_id` for persistent identity
- Enforce row-level data access by user and group membership

## 🔁 Continuous Integration (CI)

This repository uses GitHub Actions for automated continuous integration.

### Workflows
| Workflow | Path | Purpose |
|-----------|-------|----------|
| **Backend CI** | `.github/workflows/backend-ci.yml` | Installs dependencies, runs FastAPI tests, validates backend build |
| **Frontend CI** | `.github/workflows/frontend-ci.yml` | Installs dependencies, type-checks and builds React app |

Both workflows run automatically on every push or pull request.

### Pipeline Steps
1. Checkout repo
2. Install dependencies
3. Validate builds (Python / Node)
4. Run tests (if present)
5. Report status checks directly on GitHub


## 🗂️ Data Layer

The application persists model runs and results so users can retrieve status and outputs later.

**Entities**
- **Model** → defines available computational models
- **Run** → tracks each model execution instance
- **RunResult** → stores computed results and metrics

SQLite schema is automatically created on startup.
`yield_data.csv` (sample extracted from the USDA NASS Crop Yield dataset) is used for the public-model simulation.

## 🌱 Data Sources

**Public Dataset (Real)**
- The project uses a real public CSV dataset from the USDA National Agricultural Statistics Service (NASS), focusing on crop yield data for multiple states ("IA","IL","IN","OH","KS","MI") and years (2010 to 2020).
- Dataset reference: https://quickstats.nass.usda.gov/
- License: Public domain (U.S. Government work)
- A small subset of this dataset is included in the project for demonstration and local execution.

**Synthetic Dataset**
- A secondary “Water Risk Model” uses generated data to simulate environmental risk scoring and model outputs for demonstration purposes.

## 📊 Architecture & Data Model

### High-Level Architecture
See: `diagrams/architecture.png`

### Entity Relationship Diagram
See: `diagrams/erd.png`

## 🧭 Project Vision

This project demonstrates how scientific modeling workflows can be:
- automated from data entry → execution → results
- made collaborative and traceable
- integrated with user identity and access controls
- production-ready through modern CI/CD practices

It serves as a prototype for the Decision Intelligence & Digital Twin Systems vision — combining data, science, and engineering to accelerate decisions.

## 🧰 Future Enhancements
- Integration with Databricks / Unity Catalog for large-scale runs
- Model versioning and lineage tracking
- Centralized logging and monitoring (Prometheus/Grafana)
- True MSAL/Azure AD authentication
- Environment-based configuration and containerization (Docker)
- Optional deployment trigger (internal or cloud-based)

## 👩‍💻 Author
Nahida Sultana Chowdhury
