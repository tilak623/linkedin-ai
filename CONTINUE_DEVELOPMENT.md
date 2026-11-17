# Development Continuation Guide

## Current product state

The local application provides profile onboarding, skills/projects/milestones CRUD, FTS5 search/export, and persisted guided interviews. The content workflow creates an evidence-based template from saved interview/project/learning notes, lets the owner edit it, records approval, and can schedule the approved text through LinkedIn's official API after OAuth setup.

Production mode has a single-owner app-password/session gate, encrypts LinkedIn tokens at rest, and serves the React build from FastAPI. Docker uses a persistent SQLite volume. Public hosting is not configured; a stable HTTPS host and a LinkedIn Developer app with approved `w_member_social` access are required before actual publishing.

## Important constraints

- Draft generation is deterministic and does not call an AI model.
- Every LinkedIn post requires explicit approval of the exact text. Do not remove the approval step.
- The scheduled publisher requires one always-on server process. Posts more than 15 minutes late are held for review.
- This is a single-user local SQLite app. Do not scale it to multiple replicas or users.
- Never ask for or commit user passwords, OAuth client secrets, access tokens, or encryption keys.
- Research, fact-checking, media generation, GitHub analysis, calendar UI, analytics, networking, desktop integration, cloud sync, and multi-user auth are incomplete.

## Run and test

Local development instructions are in [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md). Persistent Docker and public-host requirements are in [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md).

```powershell
python -m unittest discover -s backend\tests -v
Set-Location frontend
npm.cmd run build
```

See [CURRENT_PROGRESS.md](CURRENT_PROGRESS.md) for user choices and deployment blockers.
