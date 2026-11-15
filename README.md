# O2C Revenue Assurance and Revenue Leakage Detection Platform

An enterprise-grade platform that tracks the end-to-end Order-to-Cash (O2C) lifecycle, detects financial anomalies and revenue leakage, provides explainable evidence dossiers, and benchmarks detection accuracy against an isolated ground truth.

## Project Structure

```
o2c-revenue-assurance-platform/
├── docs/
│   ├── PROJECT_REQUIREMENTS.md          # Primary Business Requirements
│   ├── SOLUTION_ARCHITECTURE.md         # Technical Solution Architecture
│   └── STAGE_1_COMPLETION_REPORT.md     # Stage 1 Verification & Report
├── backend/
│   ├── app/
│   │   ├── api/                         # FastAPI Routes (Health & Modules)
│   │   ├── core/                        # Configuration & Pydantic-Settings
│   │   ├── db/                          # SQLAlchemy Engine & Session Management
│   │   ├── models/                      # Domain Database Models
│   │   ├── schemas/                     # Pydantic v2 Request/Response Schemas
│   │   └── services/                    # Detection & Synthesis Services
│   ├── alembic/                         # Alembic Migrations
│   ├── tests/                           # Pytest Test Suite
│   ├── requirements.txt                 # Backend Python Dependencies
│   ├── .env                             # Local Environment Variables (Ignored)
│   └── .env.example                     # Environment Template
├── frontend/
│   ├── src/
│   │   ├── components/                  # UI Components (StatusCard, etc.)
│   │   ├── services/                    # API Client Services
│   │   ├── App.tsx                      # Connectivity Landing Dashboard
│   │   └── main.tsx                     # React 18 Entrypoint
│   ├── package.json                     # Frontend Node Dependencies
│   ├── vite.config.ts                   # Vite Configuration
│   ├── tailwind.config.js               # Tailwind CSS Configuration
│   ├── .env                             # Frontend Environment (VITE_API_BASE_URL)
│   └── .env.example                     # Frontend Environment Template
└── .gitignore                           # Git Secret & Artifact Ignore Rules
```

---

## Backend Setup & Execution Guide

### Prerequisites
- Python 3.11+ (Detected: Python 3.12.0)
- PostgreSQL 15+ (Detected: PostgreSQL 18 installed at `C:\Program Files\PostgreSQL\18`)

### Setup Instructions
1. Navigate to `backend/`:
   ```powershell
   cd C:\CandidateWorkspace\o2c-revenue-assurance-platform\backend
   ```
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
3. Configure `backend/.env`:
   - Open `backend/.env`
   - Update `DATABASE_URL` with your local PostgreSQL password:
     ```env
     DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/o2c_revenue_db
     ```
4. Create the target PostgreSQL database:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -c "CREATE DATABASE o2c_revenue_db;"
   ```
5. Run automated tests:
   ```powershell
   pytest
   ```
6. Start the FastAPI backend server:
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
7. Verify endpoints:
   - Application Health: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - PostgreSQL Database Health: [http://127.0.0.1:8000/health/db](http://127.0.0.1:8000/health/db)
   - Interactive Swagger API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Frontend Setup & Execution Guide

### Prerequisites
- Node.js 18+ (Detected: Node v26.5.0)
- npm 9+ (Detected: npm 10.9.0)

### Setup Instructions
1. Navigate to `frontend/`:
   ```powershell
   cd C:\CandidateWorkspace\o2c-revenue-assurance-platform\frontend
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Verify configuration in `frontend/.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
4. Start the Vite development server:
   ```powershell
   npm run dev
   ```
5. Open the web landing dashboard in your browser:
   [http://localhost:5173](http://localhost:5173)

---

## Stage Status
- **Stage 1 (Foundation Setup):** Complete. Real health and database check endpoints implemented.
- **Stage 2 (Database Schema & Models):** Pending explicit user approval.
