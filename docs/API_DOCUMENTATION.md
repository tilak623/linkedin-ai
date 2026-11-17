# REST API Documentation

Base URL: `/api/v1` (for local development, `http://localhost:8000/api/v1`).

Implemented endpoints return JSON envelopes with `success`, `data`, `error`, and `timestamp`, except redirect-based OAuth endpoints. If `APP_ADMIN_PASSWORD` is configured, API routes require the app's signed session cookie; health, login/status, and the one-use LinkedIn OAuth callback are public.

## Authentication and health

- `GET /health` — backend/database health.
- `GET /auth/me` — app session status and local profile summary.
- `POST /auth/login` — body `{"password":"..."}`; sets the HTTP-only session cookie.
- `POST /auth/logout` — clears the session cookie.

## Profile and memory

- `GET /profile`, `POST /profile/onboard`
- `/memory/skills`: `GET`, `POST`, `PATCH /{id}`, `DELETE /{id}`
- `/memory/projects`: `GET`, `POST`, `PATCH /{id}`, `DELETE /{id}`
- `/memory/milestones`: `GET`, `POST`, `PATCH /{id}`, `DELETE /{id}`
- `GET /memory/search?q={query}` — local SQLite FTS5 search.
- `GET /memory/export` — JSON export of profile and memory records.

## Guided interview

- `GET /interviews/today` — today's interview or `null`.
- `POST /interviews/start` — starts/resumes a text or voice-input session.
- `GET /interviews/{id}` — persisted transcript.
- `POST /interviews/{id}/turn` — saves an answer and returns a rule-based follow-up.
- `POST /interviews/{id}/complete` — completes the session.

The interview flow is local and rule-based; it does not call an AI model.

## Content Studio

- `GET /content/schedule` — configured daily time and time zone.
- `GET /content/posts` — saved drafts and post states.
- `POST /content/generate` — creates a factual template draft from the latest completed interview, a learning milestone, or an active project. Returns `409` if no evidence exists.
- `PATCH /content/posts/{id}` — edits title and text while the item is an unapproved draft.
- `POST /content/posts/{id}/approve` — body `{"confirm":true}` records user approval and schedules the exact text at the next daily posting time.
- `POST /content/posts/{id}/reschedule` — body `{"confirm":true}` re-approves a post that was held because its schedule was missed.

The local draft generator is deterministic, not AI-powered. Every public post requires explicit confirmation.

## LinkedIn

- `GET /linkedin/status` — OAuth configuration, connected member, and token expiry.
- `GET /linkedin/connect` — starts LinkedIn's OAuth authorization-code flow.
- `GET /linkedin/callback` — one-use state-validated callback registered with the LinkedIn Developer app.
- `DELETE /linkedin/connection` — removes the locally encrypted access token.

The scheduler publishes only explicitly approved, due posts through `POST https://api.linkedin.com/rest/posts` with the configured LinkedIn API version. Tokens are encrypted in SQLite. LinkedIn Developer app credentials and approved `w_member_social` scope are required. The scheduler requires one always-on server process and persistent local storage; posts more than 15 minutes late are held for review.

## Planned, not implemented

Technology research, AI generation/fact-checking, media generation, GitHub analysis, full content calendar, LinkedIn analytics, networking, Windows desktop integration, cloud sync, and multi-user auth are not currently exposed as implemented endpoints.
