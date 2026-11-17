# Development Continuation Guide

## What the application currently does

The current local application provides a React workspace and FastAPI backend backed by SQLite. Phase 2 supports professional-profile onboarding, skill/project/learning-milestone management, full-text search, and JSON export. The initial Phase 3 guided interview persists messages locally and supports text plus browser speech input. Other workspace areas are not yet fully implemented and may contain static sample content.

## Current architecture

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS.
- **Backend**: Python, FastAPI, Pydantic, SQLite.
- **Memory search**: SQLite FTS5, rebuilt from stored profile, skill, project, milestone, and completed-interview summary records during backend startup and updated by the APIs.
- **Interviews**: SQLite-persisted daily sessions with deterministic local follow-ups; there is no language-model call yet.
- **Current user model**: A single local default user. Authentication, cloud storage, RLS, and multi-user isolation are not implemented.
- **Not present yet**: Electron desktop app, AI service integrations, LinkedIn/GitHub integrations, cloud sync, and installer.

## Completed phases

- Phase 0: Initial discovery and planning documents.
- Phase 1: Local application foundation, health/settings endpoints, and frontend shell.
- Phase 2: Onboarding, profile persistence, skills/projects/milestones CRUD, duplicate detection, SQLite full-text search, JSON export.
- Phase 3 (partial): Local persisted interviewer, resume-today workflow, rule-based follow-ups, text input, optional browser speech input.

## Incomplete phases

- Phase 3 remaining: Explicitly consented AI-provider adapter, adaptive semantic follow-ups, voice synthesis, and expanded tests.
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
- Interview follow-ups are rule-based rather than AI-generated. Browser speech recognition support and privacy behavior vary by browser.
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

Complete Phase 3 by designing an opt-in provider interface and clear consent before interview content is sent to any external AI service. Keep the local guided flow as fallback, preserve input on provider/network failure, use only a verified free provider when configured, and add provider/API tests before enabling it. Do not claim AI generation, voice synthesis, or offline inference until implemented and tested.
