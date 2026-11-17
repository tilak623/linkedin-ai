# Development Continuation Guide

## What the application currently does

The current local application provides a React workspace and FastAPI backend backed by SQLite. Phase 2 supports professional-profile onboarding, skill/project/learning-milestone management, full-text search, and JSON export of those records. The other workspace areas are not yet fully implemented and may contain static sample content.

## Current architecture

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS.
- **Backend**: Python, FastAPI, Pydantic, SQLite.
- **Memory search**: SQLite FTS5, rebuilt from stored profile, skill, project, and milestone records during backend startup and updated by the memory API.
- **Current user model**: A single local default user. Authentication, cloud storage, RLS, and multi-user isolation are not implemented.
- **Not present yet**: Electron desktop app, AI service integrations, LinkedIn/GitHub integrations, cloud sync, and installer.

## Completed phases

- Phase 0: Initial discovery and planning documents.
- Phase 1: Local application foundation, health/settings endpoints, and frontend shell.
- Phase 2: Onboarding, profile persistence, skills/projects/milestones CRUD, duplicate detection, SQLite full-text search, JSON export.

## Incomplete phases

- Phase 3: Persisted adaptive AI interviewer (text first, voice fallback).
- Phase 4: Technology research.
- Phase 5: Content creation and approval workflow.
- Phase 6: Media generation.
- Phase 7: GitHub and portfolio intelligence.
- Phase 8: Authorized LinkedIn integration and manual fallback.
- Phase 9: Calendar and real analytics.
- Phase 10: Networking and profile recommendations.
- Phase 11: Electron desktop companion.
- Phase 12: Cloud deployment and synchronization.
- Phase 13: Reliability, end-to-end testing, and Windows installer.

## Known limitations

- Current API routes use a fixed local user ID; do not expose this backend as a multi-user service.
- AI and external integrations are not active. API keys are not required for Phase 2.
- The memory export contains only profile, skills, projects, and learning milestones.
- Some non-memory workspace pages still use static sample data.

## Environment variables

No environment variables are required for the local Phase 2 workflows. Optional server settings are documented in `docs/SETUP_GUIDE.md`. Do not commit `.env` files or API keys.

## Start the application

Backend terminal:

```powershell
cd backend
python -m pip install -r requirements.txt
python run.py
```

Frontend terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`; backend API docs are at `http://localhost:8000/docs`.

## Run tests

```powershell
python -m unittest discover -s backend/tests -v
```

```powershell
cd frontend
npm.cmd run build
```

## Exact next development step

Start Phase 3 by implementing persisted interview sessions and messages, then a text-based adaptive interviewer behind a provider interface. Keep responses evidence-grounded, preserve user input on provider/network failure, use a free provider only when configured, and add API tests before connecting the interview UI. Do not claim voice synthesis, AI generation, or offline inference until implemented and tested.
