# GenAI Startup Analyst MVP

This repository contains a full-stack prototype of an AI-powered startup analyst that ingests founder material and public data to generate investor-ready insights. The system is designed to orchestrate Google Cloud services (Gemini/Vertex AI, Cloud Vision, BigQuery, Firebase) to build actionable deal notes and founder dossiers.

## Architecture

```
frontend/ (Vite + React + TypeScript)
backend/  (FastAPI, Google Cloud SDKs)
```

Key backend capabilities:
- **Document ingestion** with multi-format parsing (PDF, DOCX, PPTX, XLSX, CSV, JSON, images via Cloud Vision OCR).
- **Agentic workflow** that aggregates founder material, public signals (BigQuery), and investor preferences.
- **Gemini / Vertex AI** prompts for summary, detailed memo, and founder profile generation with graceful fallbacks when credentials are absent.
- **Scoring engine** that applies customizable investor weightings across market, team, traction, technology, financials, and regulatory axes.
- **Report builder** that exports summary, detailed, and founder profile PDFs. Artifacts can be pushed to Firebase Storage when configured.

Frontend highlights:
- Drag-and-drop multi-file uploader.
- Investor preference calibration sliders (0–100%) per diligence axis.
- Startup context capture (sector, HQ, description, analyst notes).
- Real-time presentation of scores, strengths, risks, AI-generated notes, and downloadable PDFs.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud project with Vertex AI, Cloud Vision, BigQuery, and Firebase enabled (optional for offline testing).

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Environment variables (set via `.env` or shell):

- `GOOGLE_PROJECT_ID`
- `GOOGLE_LOCATION` (default: `us-central1`)
- `VERTEX_MODEL` (default: `gemini-1.5-pro`)
- `BIGQUERY_DATASET`
- `FIREBASE_STORAGE_BUCKET`
- `ENABLE_GOOGLE_SERVICES` (`true`/`false`)

When variables are not provided, the backend runs with heuristic fallbacks so the UI remains usable in offline mode.

Run backend tests:

```bash
cd backend
pytest
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API calls to `http://localhost:8000`.

## Connecting Google Cloud Services

1. Authenticate using `gcloud auth application-default login`.
2. Ensure the following APIs are enabled: Vertex AI, Vision, BigQuery, Firebase Storage.
3. Populate `.env` in `backend/` with project settings and restart the FastAPI server.

## Agentic Workflow

1. **Ingestion Agent** saves documents locally (and to Firebase when configured) and extracts text.
2. **Signal Aggregator Agent** pulls sector benchmarks and public signals from BigQuery.
3. **Reasoning Agent (Gemini)** synthesizes concise and detailed deal notes plus founder dossiers informed by investor weightings.
4. **Reporting Agent** assembles structured PDFs and exposes download links to the UI.

## Deployment Notes

- Containerize backend and frontend separately or serve frontend build via a CDN.
- Configure Cloud Run or GKE for backend with attached service accounts.
- Use Firebase Hosting for frontend to leverage Firebase Storage signed URLs for report distribution.

## Disclaimer

This is an MVP. Integrations assume correct Google Cloud credentials and datasets. Customize prompts, benchmarks, and scoring logic for production use.
