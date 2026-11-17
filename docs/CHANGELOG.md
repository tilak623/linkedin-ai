# Changelog

All notable changes to the **Personal Branding AI Agent** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - Approval-gated LinkedIn publishing

### Added
- Production single-owner app-password sessions and protected API routes.
- Evidence-based local draft creation, draft editing, explicit approval audit, and scheduled post states.
- LinkedIn OAuth callback with one-use state validation and encrypted local access-token storage.
- Official LinkedIn Posts API text publishing and single-instance daily scheduler with missed-post review protection.
- Docker build and persistent SQLite volume configuration.
- Focused tests for login protection, evidence-only drafts, approval, scheduling, token encryption, and LinkedIn request headers.

### Limitations
- Public hosting, LinkedIn Developer app credentials, and approved member-posting scope are not configured.
- The draft generator is deterministic, not AI; several product roadmap modules remain unimplemented.

## [Unreleased] - Free-tier deployment support

### Added
- PostgreSQL connection support alongside the local SQLite default.
- A bearer-token protected external scheduler endpoint and GitHub Actions daily trigger.
- A Render free-tier Blueprint for a best-effort deployment without a persistent disk.

### Limitations
- Free-tier sleep and scheduled-workflow delays can cause posts to be held for review.
- A PostgreSQL provider, Render service, GitHub secrets, and LinkedIn Developer app still need to be configured by the account owner.

## [Unreleased] - Phase 2: Professional Memory and Onboarding

### Added
- First-run onboarding for the local professional profile and initial skill records.
- CRUD API and UI workflows for skills, projects, and learning milestones.
- SQLite FTS5 search, duplicate name/title checks, and JSON export for profile and memory records.
- Database migration for the onboarding-completion flag.
- API tests covering onboarding, CRUD, duplicate detection, search/index rebuild, URL validation, and export.
- `.gitignore` rules for local environment files, databases, caches, dependencies, and frontend build output.

### Changed
- Clarified which product features are planned versus currently implemented in the README and architecture/security/privacy documentation.

## [Unreleased] - Phase 3: Local Guided Interview

### Added
- Persistent daily interview sessions with text and optional browser speech input.
- Resume-today, rule-based follow-up selection, manual completion, and no-post handling.
- API tests for saved turns, adaptive prompts, completion, and no-progress days.

### Limitations
- The interviewer does not call an AI model and does not synthesize speech. Provider use requires a later consent-gated integration.

## [0.2.0] - 2026-11-17 (Phase 1: Functional Application Foundation)

### Added
- **Backend Foundation (FastAPI + Python 3.13)**:
  - Centralized Pydantic v2 configuration with CORS support (`backend/app/core/config.py`).
  - Structured logging and unified exception handling (`backend/app/core/errors.py`, `backend/app/core/logging_config.py`).
  - Zero-lock embedded SQLite connection manager with atomic rollback journaling (`backend/app/core/db.py`).
  - System health, telemetry, settings, and auth endpoints (`/api/v1/health`, `/api/v1/settings`, `/api/v1/auth/me`).
  - Automated unit test suite (`backend/tests/test_api.py`) passing 100% (6/6 tests).
- **Frontend Foundation (React 18 + TypeScript + Vite + Tailwind CSS)**:
  - 12-section workspace navigation shell covering Command Center, AI Interview, Content Studio, Media Studio, Calendar, Research, Memory, Portfolio, Networking, Analytics, Profile, and Settings.
  - Web Speech API integration structure for low-latency in-browser daily standups.
  - Live hardware telemetry badge reporting available RAM and CPU cores.
  - Custom Obsidian Dark and Clean Light design system.
  - Production build passing cleanly (`dist/` built in 8.15s).

---

## [0.1.0] - 2026-11-16 (Phase 0: Technical Discovery & Planning)

### Added
- Comprehensive system architecture specification (`docs/ARCHITECTURE.md`).
- Multi-user isolated relational database schema for Supabase Postgres and local SQLite (`docs/DATABASE_SCHEMA.md`).
- Complete REST API contract definitions (`docs/API_DOCUMENTATION.md`).
- Local and cloud deployment guides (`docs/SETUP_GUIDE.md`, `docs/DEPLOYMENT_GUIDE.md`).
- Security and Privacy policies (`docs/SECURITY.md`, `docs/PRIVACY.md`).
- Master 14-phase development roadmap (`docs/DEVELOPMENT_ROADMAP.md`).
- Testing and diagnostic documentation (`docs/TESTING.md`, `docs/TROUBLESHOOTING.md`).
- Progress tracking and session continuation mechanisms (`CURRENT_PROGRESS.md`, `CONTINUE_DEVELOPMENT.md`).
