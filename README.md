# Personal Branding AI Agent (LinkedIn Focus)

An intelligent, authentic, and zero-cost AI-powered personal branding assistant that transforms your daily engineering activities, technical learning, code repositories, and career milestones into a credible and consistent professional presence on LinkedIn.

> **Development status:** The local app includes onboarding and memory, a persisted guided interview, evidence-based post drafts, app-password protection for production, LinkedIn OAuth, and an approval-gated daily publishing scheduler. Draft creation is deterministic and does not call an AI model. Research, media, GitHub analysis, analytics, networking, desktop support, and cloud sync are not implemented. Public deployment and LinkedIn posting require your own HTTPS host and LinkedIn Developer app; no service accounts or secrets are included.

---

## 🌟 Product Vision

1. **AI Daily Interviewer (Voice & Text)**: A local guided, persisted interview flow is available; language-model reasoning and speech synthesis are planned.
2. **Professional Memory & Knowledge Library**: Local profile, skills, projects, and learning milestones are implemented; adaptive memory features remain planned.
3. **Technology Research Engine**: Multi-source daily tech intelligence (Hacker News, Reddit, ArXiv, GitHub Trending, tech publications) with automated credibility ranking and claim verification.
4. **Evidence-based Content Studio**: Local post drafts from saved interview, project, or learning evidence; edit and approve before scheduling. No AI or fact-checking provider is connected.
5. **AI Media Generation Studio**: Programmatic, high-resolution infographic, architecture diagram, code snippet, and carousel generation (100% free, zero paid subscriptions).
6. **LinkedIn Publishing Manager**: Official OAuth and Posts API integration, encrypted token storage, explicit per-post approval, and scheduled publishing when configured.
7. **Smart Content Calendar & Analytics**: Best-time scheduling recommendations, draft status tracking, and genuine engagement metrics without fabricated data.
8. **GitHub & Portfolio Intelligence**: Repository analyzer that extracts real engineering contributions without exaggeration.
9. **Professional Networking Assistant**: Intelligent suggestion engine for relevant peer connections and thoughtful discussion contributions with explicit approval gates.
10. **Windows Desktop Companion**: Electron tray app with automated startup, 15-minute gentle interview reminders, local folder scanning, and offline SQLite caching.
11. **Privacy & Security Centre**: Complete data ownership, local-first credential storage, zero secret leaks, and granular folder permissions.
12. **Cost-conscious Architecture**: Local SQLite and deterministic draft generation work without paid API keys; public hosting and LinkedIn developer access depend on external providers and their current policies.

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

### Local development

Start the backend from the repository root:
```bash
python -m pip install -r backend/requirements.txt
python backend/run.py
```

In another terminal:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The development server proxies API calls to the local backend. The Electron desktop companion is not included.

### Private Docker deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for the persistent local Docker setup and the requirements for public hosting. Never commit `.env` or paste secrets into chat.

---

## 🛡️ Core Principles

- **Authenticity First**: Never invent achievements, fake project metrics, or generate robotic hype posts.
- **Strict Human Approval**: A LinkedIn post is not scheduled until the user explicitly approves its exact text. Comments, connection requests, and profile edits are not automated.
- **Local-first Operation**: The implemented interview, memory, and draft workflows run without external AI APIs; public hosting and LinkedIn API access have separate provider requirements.
- **Privacy & Security**: Read-only local file inspection with explicit user authorization; no private tokens committed or leaked.

---

## 📖 Documentation Index

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Complete system design & data flows
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Supabase Postgres & SQLite schema
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - Complete REST API contract
- [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Local development & environment setup
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Persistent Docker and public-host requirements
- [SECURITY.md](docs/SECURITY.md) - Security policies & credential management
- [PRIVACY.md](docs/PRIVACY.md) - Privacy protections & user data controls
- [TESTING.md](docs/TESTING.md) - Test strategy, unit & integration test guides
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues & fixes
- [CHANGELOG.md](docs/CHANGELOG.md) - Project version history
- [DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md) - 14-phase roadmap
- [CURRENT_PROGRESS.md](CURRENT_PROGRESS.md) - Current development progress tracker
- [CONTINUE_DEVELOPMENT.md](docs/CONTINUE_DEVELOPMENT.md) - Session continuation instructions
