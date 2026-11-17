# Deployment Guide

## Deployment requirements

This is a private, single-owner service backed by SQLite. It is not safe to deploy publicly without production app-password/session secrets. Daily jobs run inside the web process; the host must remain awake, retain `/data`, and run exactly one app instance. No hosting provider or LinkedIn Developer app is configured in this repository.

## Run with persistent Docker storage

1. Install Docker Desktop and create a private `.env` from `.env.example`.
2. Generate secrets locally (do not send them in chat):

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

   Use the first value for `APP_SESSION_SECRET`; set `APP_ADMIN_PASSWORD` to a long, unique password; use the second value for `LINKEDIN_TOKEN_ENCRYPTION_KEY`.
3. Before connecting LinkedIn, create a LinkedIn Developer app and request `openid`, `profile`, and `w_member_social` access. Configure an exact HTTPS callback in the Developer app and `.env`:

   `https://YOUR-HOST/api/v1/linkedin/callback`

   Set `LINKEDIN_FRONTEND_URL` to `https://YOUR-HOST`. LinkedIn may require product approval for member posting. A local `http://localhost` callback is not a substitute for the required public HTTPS callback.
4. Start the app:

   ```powershell
   docker compose up --build -d
   ```

5. Open `http://localhost:8000` and sign in with `APP_ADMIN_PASSWORD`. Docker Compose stores SQLite in the persistent `brand_agent_data` volume.

The scheduler creates a daily draft at the configured time when saved evidence exists. Every post requires explicit approval before it is scheduled. Approved posts more than 15 minutes late are held for review rather than published as catch-up. Back up the Docker volume and keep the encryption key; losing it makes saved LinkedIn tokens unusable.

LinkedIn tokens expire. Reconnect through the Content Studio after expiry; automatic token refresh is not implemented.

## Public hosting requirements

Choose a host that supports:

- An always-on, single Docker instance with HTTPS and a stable callback URL.
- A persistent writable disk mounted at `/data`.
- Secure environment-variable/secret configuration for the app password, session key, LinkedIn OAuth credentials, and token-encryption key.
- No automatic multi-replica scaling; SQLite and the in-process scheduler require one instance.

Configure the host using the `Dockerfile` and variables in `.env.example`. The current workspace has no hosting account or LinkedIn Developer app, and Docker is not installed here, so a public service cannot be provisioned or verified from this repository alone. Do not use a host that sleeps or discards its filesystem for this scheduled-publishing workload. Never paste passwords, API keys, or OAuth tokens into chat or commit them to Git.
