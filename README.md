# UAE HR Portal

A minimal HR portal application for UAE.

## Project Structure

```
hr-command-center/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
└── docs/            # Documentation
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will be available at http://localhost:3000

## Documentation

See the [docs](./docs) folder for detailed documentation.

## Features

This is a minimal scaffold with:
- Backend: FastAPI with `/health` endpoint
- Frontend: React with placeholder Home and About pages
- Documentation structure

Features will be added in future iterations.