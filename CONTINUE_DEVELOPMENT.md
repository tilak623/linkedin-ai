# Development Continuation Guide

This document maintains complete execution context for the **Personal Branding AI Agent**, ensuring continuity across sessions and Antigravity context limits.

---

## 1. What the Application Does

The Personal Branding AI Agent is an authentic, intelligent branding manager focused on LinkedIn. It conducts adaptive daily voice/text interviews to learn what you worked on, tracks your skills and projects with accurate proficiency distinctions, researches industry breakthroughs daily from credible sources, drafts human-sounding LinkedIn posts, programmatically renders infographics and carousels, manages publishing with mandatory human approval, and provides a Windows desktop tray companion with gentle interview reminders.

---

## 2. Current Architecture

- **Desktop Layer**: Windows Electron tray app handling background reminders (15-min intervals), local file folder selection with read-only security, and offline SQLite caching.
- **Frontend Layer**: React 18 + TypeScript + Vite single-page application featuring 12 dedicated workspaces, dark/light theme toggle, and Web Speech API voice capture.
- **Backend Layer**: Python 3.13 + FastAPI + Uvicorn + Pydantic v2 async REST API providing modular endpoints for interviews, memory, research, content generation, and publishing.
- **AI Engine Layer**: Hybrid zero-cost multi-provider engine:
  - Cloud: Google Gemini 2.5 Flash / Groq (Llama 3.3 70B) Free Tiers for reasoning, interviewing, and writing.
  - Local/Offline: Quantized CPU SLMs (e.g., Qwen2.5-1.5B / SmolLM2-1.7B) sized strictly within the system's ~4GB available RAM budget.
- **Data & Auth Layer**:
  - Cloud: Supabase PostgreSQL with Row Level Security (RLS) enforcing multi-user data isolation.
  - Local: Embedded SQLite database (`brand_agent.db`) with zero-lock connection pooling for zero-network offline functionality.

---

## 3. Selected Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Desktop**: Electron, Node.js
- **Backend**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, HTTPX, Pillow, SQLite3
- **Database**: SQLite (Local Embedded) + Supabase (Cloud Postgres)
- **Voice**: Web Speech API (Browser/Electron Native) + Windows SAPI fallback
- **Cost**: $0.00 / Zero-Cost Strict Architecture

---

## 4. Completed Phases

- **Phase 0 (Technical Discovery and Planning)**: Completed.
  - Environment audited: 14-core Intel CPU, 16GB RAM, integrated Intel GPU, 840GB free SSD.
  - Python 3.13 and Node.js v24 runtimes verified.
  - Official LinkedIn API boundaries analyzed (`w_member_social` direct posting vs manual browser-assisted fallback).
  - Multi-user isolated database schema designed.
  - 14-file documentation suite established.
- **Phase 1 (Functional Application Foundation)**: Completed.
  - Python FastAPI backend live with health, settings, auth, and database endpoints.
  - SQLite zero-lock connection manager configured and seeded.
  - Automated unit test suite passing 100% (6/6 tests).
  - React 18 + TypeScript + Tailwind CSS frontend fully built and verified with production build (12 workspace views).

---

## 5. Incomplete Phases

- Phase 2: Professional Memory & Onboarding Wizard (Next)
- Phase 3: AI Interviewer (Voice & Text)
- Phase 4: AI Technology Research Engine
- Phase 5: Content Creation Studio
- Phase 6: Media Generation Studio
- Phase 7: GitHub and Portfolio Intelligence
- Phase 8: LinkedIn Integration & Publishing
- Phase 9: Smart Calendar and Analytics
- Phase 10: Networking and Profile Optimization
- Phase 11: Windows Desktop Companion (Electron)
- Phase 12: Cloud Deployment and Synchronization
- Phase 13: Final Testing, Reliability & Windows Installer

---

## 6. Current Bugs

None.

---

## 7. Outstanding Tasks

1. Begin **Phase 2: Professional Memory & Onboarding Wizard**:
   - Implement onboarding wizard for career direction, skills, and writing voice.
   - Implement backend endpoints for skill CRUD with strict 4-level proficiency verification (*implemented*, *studied*, *explored*, *discovered*).
   - Implement project tracking and milestone ingestion endpoints.
   - Add full-text search and duplicate-topic detection to the knowledge library.

---

## 8. Required Environment Variables

When running locally, store in `.env` or `backend/.env`:
```env
# Server
PORT=8000
HOST=127.0.0.1
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

# Database (Supabase Free Tier - Optional)
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=sqlite:///./brand_agent.db

# Free AI Providers (Zero Cost)
GEMINI_API_KEY=
GROQ_API_KEY=
```

---

## 9. How to Start the Application

### Start Backend
```powershell
cd backend
python run.py
# API runs at http://127.0.0.1:8000
# Interactive API docs at http://127.0.0.1:8000/docs
```

### Start Frontend
```powershell
cd frontend
npm.cmd run dev
# Web app runs at http://127.0.0.1:5173
```

---

## 10. How to Run Tests

### Backend Tests
```powershell
python -m unittest backend/tests/test_api.py
```

### Frontend Build Verification
```powershell
cd frontend
npm.cmd run build
```

---

## 11. The Exact Next Development Step

Proceed to **Phase 2: Professional Memory & Onboarding Wizard**:
1. Create `backend/app/api/v1/memory.py` with endpoints for skills, projects, learning milestones, and full-text search.
2. Build the interactive Onboarding Wizard in the frontend to guide new users through career goals, skills, and writing style preferences.
3. Wire the Memory and Portfolio pages to live API endpoints.
4. Add automated tests for skill level transitions and search duplicate detection.
