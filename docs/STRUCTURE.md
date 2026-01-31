# Project Structure

This document describes the minimal scaffold structure for the UAE HR Portal.

## Directory Layout

```
hr-command-center/
├── backend/              # FastAPI backend application
│   ├── main.py          # Main application with /health endpoint
│   ├── requirements.txt # Python dependencies
│   ├── README.md        # Backend setup instructions
│   └── .gitignore       # Python/venv exclusions
│
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── pages/      # Page components
│   │   │   ├── Home.js
│   │   │   └── About.js
│   │   ├── App.js      # Main app component with routing
│   │   ├── App.css     # Global styles
│   │   └── index.js    # React entry point
│   ├── public/
│   │   └── index.html  # HTML template
│   ├── package.json    # npm dependencies
│   ├── README.md       # Frontend setup instructions
│   └── .gitignore      # Node/build exclusions
│
└── docs/                # Documentation
    ├── README.md        # Documentation overview
    └── STRUCTURE.md     # This file
```

## Backend Details

**Technology**: FastAPI + Uvicorn

**Endpoints**:
- `GET /health` - Returns `{"status": "healthy"}`
- `GET /docs` - Auto-generated Swagger UI documentation

**Port**: 8000

## Frontend Details

**Technology**: React 18 + React Router

**Pages**:
- `/` - Home page with welcome message
- `/about` - About page with app description

**Port**: 3000 (default for React)

## Documentation

The `docs/` folder contains project documentation including:
- Setup instructions
- Architecture overview
- API documentation (to be added)
- User guides (to be added)

## Notes

- This is a **minimal scaffold** with no business logic
- No authentication or authorization implemented
- No database connections
- No complex features or dashboards
- Files are intentionally small and readable
- Ready for future feature development
