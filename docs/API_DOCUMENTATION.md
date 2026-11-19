# REST API Documentation

Base URL: `/api/v1` (for local development, `http://localhost:8000/api/v1`).

Implemented endpoints return JSON envelopes with `success`, `data`, `error`, and `timestamp`, except redirect-based OAuth endpoints. If `APP_ADMIN_PASSWORD` is configured, API routes require the app's signed session cookie; health, login/status, the one-use LinkedIn OAuth callback, and the scheduler trigger are public at the session layer. The scheduler trigger has its own bearer-token check.

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
- `GET /memory/search?q={query}` — searches the local SQLite or configured PostgreSQL knowledge index.
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
- `POST /content/humanize` — sends provided interview notes to the selected Gemini or Groq provider and creates an editable draft. Requires that provider's API key and online mode.
- `PATCH /content/posts/{id}` — edits title and text while the item is an unapproved draft.
- `GET /content/posts/{id}/media`, `POST /content/posts/{id}/media` — list or attach one JPEG, PNG, or GIF image (maximum 10 MB) to a draft. `DELETE /content/posts/{id}/media/{asset_id}` removes it.
- `GET /content/media/{asset_id}` — serves the authenticated image preview.
- `POST /content/posts/{id}/approve` — body `{"confirm":true}` records user approval and schedules the exact text at the next daily posting time.
- `POST /content/posts/{id}/reschedule` — body `{"confirm":true}` re-approves a post that was held because its schedule was missed.
- `POST /content/scheduler/tick` — external scheduler hook; requires `Authorization: Bearer <SCHEDULER_TRIGGER_TOKEN>`.

Evidence-based draft generation is deterministic. Humanized drafts use the configured external AI provider and only become editable drafts; every public post still requires explicit confirmation. Attached images are stored in the database and uploaded to LinkedIn at publishing time.

## LinkedIn

- `GET /linkedin/status` — OAuth configuration, connected member, and token expiry.
- `GET /linkedin/connect` — starts LinkedIn's OAuth authorization-code flow.
- `GET /linkedin/callback` — one-use state-validated callback registered with the LinkedIn Developer app.
- `DELETE /linkedin/connection` — removes the locally encrypted access token.

The scheduler publishes only explicitly approved, due posts through `POST https://api.linkedin.com/rest/posts` with the configured LinkedIn API version. Tokens are encrypted in the configured database. LinkedIn Developer app credentials and approved `w_member_social` scope are required. For free hosting, GitHub Actions can call the external scheduler hook; timing is best effort, and posts more than 15 minutes late are held for review.

## Planned, not implemented

Technology research and fact-checking, media generation, GitHub analysis, full content calendar, LinkedIn analytics, networking, Windows desktop integration, cloud sync, and multi-user auth are not currently exposed as implemented endpoints.
