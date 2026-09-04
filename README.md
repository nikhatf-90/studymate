# StudyMate AI

StudyMate AI is an AI-powered student productivity platform for the Week 4 Innovation Hacks internship capstone. It keeps student data private, analyses marks and attendance, identifies priorities, creates a study schedule, records progress, and provides Gemini-powered study assistance.

## Features

- JWT authentication with bcrypt password hashing and protected routes.
- Student profile, subject CRUD, marks, attendance, difficulty, exam dates, and progress.
- Educational performance estimates with category, confidence, and risk—not scientifically validated forecasts.
- Weak-subject prioritisation, regenerable study plans, sessions, and analytics charts.
- Gemini chat and question generation. Missing configuration causes a clear error; AI output is never faked.
- SQLite development database, Docker, tests, and a responsive React/Vite UI.
- New accounts receive clearly named removable **Sample:** subjects for an immediate dashboard demo.

## Architecture

```text
Student → React + Vite + Recharts → FastAPI (JWT and validation)
                                         ├─ SQLite / SQLAlchemy
                                         ├─ ML prediction pipeline (joblib)
                                         └─ Gemini API (server-side key)
```

See [architecture notes](docs/architecture.md).

## Install and run

To launch both local servers after installation, run `./start-studymate.ps1` from the project root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`; interactive API docs are at `http://localhost:8000/docs`.

## Environment and Gemini

Copy `.env.example` to `.env`. Set `JWT_SECRET` to a unique random value. Set `GEMINI_API_KEY` to enable chat and question generation; this secret is only read by the backend. The rest of the application works without it.

## ML methodology

`ml/train.py` makes a reproducible synthetic demonstration dataset, uses a fixed train/test split, compares Random Forest and Gradient Boosting with MAE, RMSE, and R², then saves the lowest-MAE model.

```powershell
python ml/train.py
```

Synthetic data is for demonstrations only. Validate on representative, consented data before using any model in academic decisions.

## Test

```powershell
cd backend
pytest tests -q
```

Tests cover registration/login, protected routes, and invalid input. In the UI, register, add subjects, generate a plan and estimates, log a session, then configure Gemini to test AI features.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The frontend is on port 5173 and the backend on port 8000.

## Endpoint overview

`POST /api/auth/register`, `POST /api/auth/login`, `GET|PUT /api/profile`, `GET|POST /api/subjects`, `PUT|DELETE /api/subjects/{id}`, `POST|GET /api/predictions`, `POST|GET /api/study-plan`, `PUT|DELETE /api/study-plan/{id}`, `POST /api/ai/chat`, `POST /api/questions/generate`, `POST /api/study-session`, `GET /api/progress`, and `GET /api/analytics`.

## Deployment, screenshots, and future scope

Add dashboard, planner, and analytics screenshots after deployment. For production use HTTPS, a managed database, a unique JWT secret, explicit CORS origins, and securely managed Gemini credentials. Future improvements include model monitoring, calendars/reminders, rate limiting, and a validated real-data model.
