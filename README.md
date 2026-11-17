# Personal Branding AI Agent (LinkedIn Focus)

An intelligent, authentic, and zero-cost AI-powered personal branding assistant that transforms your daily engineering activities, technical learning, code repositories, and career milestones into a credible and consistent professional presence on LinkedIn.

> **Development status:** This repository currently contains the local FastAPI/SQLite and React foundation, professional onboarding, and persistent profile/skills/projects/milestones memory with full-text search. The features below describe the product vision; most integrations and workspaces are still planned and should not be considered implemented.

---

## 🌟 Product Vision

1. **AI Daily Interviewer (Voice & Text)**: Planned adaptive interviews to capture what you built, learned, solved, or observed.
2. **Professional Memory & Knowledge Library**: Local profile, skills, projects, and learning milestones are implemented; adaptive memory features remain planned.
3. **Technology Research Engine**: Multi-source daily tech intelligence (Hacker News, Reddit, ArXiv, GitHub Trending, tech publications) with automated credibility ranking and claim verification.
4. **AI Content Creation Studio**: Context-aware draft generator with authentic human tone, strict anti-cliché filters, fact-checking verification, and mandatory human approval workflow.
5. **AI Media Generation Studio**: Programmatic, high-resolution infographic, architecture diagram, code snippet, and carousel generation (100% free, zero paid subscriptions).
6. **LinkedIn Publishing Manager**: Hybrid integration using authorized LinkedIn REST APIs (`w_member_social`) and elegant browser-assisted manual fallbacks where APIs are restricted.
7. **Smart Content Calendar & Analytics**: Best-time scheduling recommendations, draft status tracking, and genuine engagement metrics without fabricated data.
8. **GitHub & Portfolio Intelligence**: Repository analyzer that extracts real engineering contributions without exaggeration.
9. **Professional Networking Assistant**: Intelligent suggestion engine for relevant peer connections and thoughtful discussion contributions with explicit approval gates.
10. **Windows Desktop Companion**: Electron tray app with automated startup, 15-minute gentle interview reminders, local folder scanning, and offline SQLite caching.
11. **Privacy & Security Centre**: Complete data ownership, local-first credential storage, zero secret leaks, and granular folder permissions.
12. **Strictly Free Architecture**: Zero paid APIs. Fully operational on Google Gemini Free Tier, Groq Free Tier, Web Speech API, Supabase Free Tier, and local quantized SLMs.

---

## 📁 Repository Structure

```
├── backend/                  # Python FastAPI application
│   ├── app/
│   │   ├── api/v1/           # Health, settings, profile, and memory endpoints
│   │   ├── core/             # Configuration, SQLite, errors, and logging
│   │   └── models/           # Pydantic request/response schemas
│   ├── tests/                # Backend unit and API tests
│   ├── requirements.txt      # Python dependencies
│   └── run.py                # Backend server entrypoint
├── frontend/                 # React + TypeScript + Vite web workspace
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Workspace views
│   │   ├── services/         # Backend API client
│   │   └── types/            # TypeScript interfaces
│   └── package.json          # Frontend dependencies
└── docs/                     # Full system specifications & guides
```

---

## 🚀 Quick Start

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for full installation and launch instructions.

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The Electron desktop companion is part of the future roadmap and is not included in the current repository.

---

## 🛡️ Core Principles

- **Authenticity First**: Never invent achievements, fake project metrics, or generate robotic hype posts.
- **Strict Human Approval**: Every public action (posts, comments, connection requests, profile edits) requires explicit user confirmation.
- **Strictly Free Operation**: Designed from the ground up to never require paid API keys, paid hosting, or hidden subscriptions.
- **Privacy & Security**: Read-only local file inspection with explicit user authorization; no private tokens committed or leaked.

---

## 📖 Documentation Index

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Complete system design & data flows
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Supabase Postgres & SQLite schema
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - Complete REST API contract
- [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Local development & environment setup
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Free-tier cloud deployment guide
- [SECURITY.md](docs/SECURITY.md) - Security policies & credential management
- [PRIVACY.md](docs/PRIVACY.md) - Privacy protections & user data controls
- [TESTING.md](docs/TESTING.md) - Test strategy, unit & integration test guides
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues & fixes
- [CHANGELOG.md](docs/CHANGELOG.md) - Project version history
- [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) - 14-phase roadmap
- [CURRENT_PROGRESS.md](docs/CURRENT_PROGRESS.md) - Real-time development progress tracker
- [CONTINUE_DEVELOPMENT.md](docs/CONTINUE_DEVELOPMENT.md) - Session continuation instructions
