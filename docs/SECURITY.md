# Security Policy & Architecture

> **Status:** Production app-password/session protection and encrypted LinkedIn token storage are implemented. SQLite is the local default; a single-owner PostgreSQL connection is supported for hosting. Cloud RLS, multi-user isolation, and an Electron/local-folder scanner are not implemented.

## Credentials and keys

- Keep `.env`, API keys, OAuth tokens, and passwords out of Git.
- Production secrets are provided only through environment variables or the host's secret manager.
- LinkedIn access tokens are encrypted in the configured database with a separate Fernet key from `LINKEDIN_TOKEN_ENCRYPTION_KEY`.
- Production requires an app password of at least 16 characters and a session-signing secret of at least 32 characters. Sessions use an HTTP-only, SameSite=Lax cookie that is Secure in production.
- The external scheduler hook uses a separate `SCHEDULER_TRIGGER_TOKEN`; store the same value in the host's secret settings and the GitHub Actions repository secret.
- Do not deploy the single-owner app as a multi-user service.

## Publishing approval boundary

- The app does not generate and publish posts without review. The user must approve the exact post text before it can be scheduled.
- The scheduled publisher only publishes approved posts. Posts more than 15 minutes late are held for review.
- Comments, connection requests, and profile edits are not automated.
- Disconnecting LinkedIn removes the app's local encrypted token; revoke the app grant from LinkedIn account settings if access must be revoked immediately.

## Deployment limitations

- Use HTTPS and production secrets. For free-tier hosting, use PostgreSQL instead of ephemeral local SQLite storage, disable the in-process scheduler, and restrict the scheduler hook with its bearer token.
- Free hosting and scheduled workflows can sleep or be delayed; the daily publisher is best effort, not guaranteed at an exact minute.
- The current app does not implement cloud synchronization, row-level security, or multi-user authorization.
- Local file scanning and external AI data sharing are not implemented.

## Local file system

No automatic folder scanning is implemented. Any future scanner must require explicit directory authorization and read-only access. Before sending extracted user text to an external AI provider, the UI must obtain explicit consent.
