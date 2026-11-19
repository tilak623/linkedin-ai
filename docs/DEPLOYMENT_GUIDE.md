# Deployment Guide

## Free-tier deployment (best effort)

The repository includes a Render Blueprint in `render.yaml` and a scheduled GitHub Actions workflow. The app can use PostgreSQL in production while retaining SQLite for local development. This setup avoids a paid persistent disk, but it does **not** guarantee the site will always be awake or that a daily job will run at an exact minute. Treat free-tier scheduling as best effort, not business-critical automation.

### 1. Create a PostgreSQL database

Create a PostgreSQL database with a provider that offers a free tier, such as [Neon](https://neon.tech/). Copy its PostgreSQL connection URL directly into Render's secret field when prompted. Keep the URL private and use the provider's SSL-enabled connection string.

### 2. Create the Render service

1. In Render, choose **New → Blueprint** and connect this GitHub repository.
2. Render reads `render.yaml` and proposes a free Docker web service.
3. Enter the requested secret values in Render:
   - `DATABASE_URL`: the PostgreSQL connection URL from step 1.
   - `APP_ADMIN_PASSWORD`: a unique password with at least 16 characters.
   - `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, and `LINKEDIN_TOKEN_ENCRYPTION_KEY` when enabling LinkedIn publishing.
   - Render generates `APP_SESSION_SECRET` and `SCHEDULER_TRIGGER_TOKEN` for this Blueprint. If you set them manually, use separate random values with at least 32 characters.
4. Review the plan before creating the service. The Blueprint disables the in-process scheduler because the free web service can sleep.
5. After deployment, open the service URL and confirm the health endpoint reports `postgresql (connected)`.

Generate the admin password locally. Render generates the session and scheduler secrets; if you set those manually, generate separate random values. Do not share secrets in chat or commit them:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 3. Configure the GitHub scheduled trigger

In the repository's **Settings → Secrets and variables → Actions**, add:

- `SCHEDULER_TRIGGER_TOKEN`: copy the generated value from the Render service's environment settings.

The workflow uses `https://linkedin-ai-publisher.onrender.com` by default, so `APP_URL` is not required for this deployment. If you use a different Render URL or custom domain, set `APP_URL` as a repository secret to override it. The workflow at `.github/workflows/daily-linkedin-scheduler.yml` calls the protected scheduler endpoint daily at **03:30 UTC (09:00 Asia/Kolkata)** and can also be started manually from the Actions tab. GitHub scheduled workflows can be delayed; if a due post is more than 15 minutes late, the app holds it for review instead of publishing it late.

### 4. Enable LinkedIn publishing

Create a LinkedIn Developer app and obtain the approved `openid`, `profile`, and `w_member_social` access. In Render, set `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, and `LINKEDIN_TOKEN_ENCRYPTION_KEY`. Generate the encryption key locally:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

In the LinkedIn app, configure this exact HTTPS callback:

`https://linkedin-ai-publisher.onrender.com/api/v1/linkedin/callback`

After adding or changing OAuth settings, reconnect LinkedIn from the deployed Content Studio and verify the authorized profile. The app still requires explicit approval of each exact post before scheduling. LinkedIn access may require product review; hosting does not grant API access.

Keep the encryption key stable. Losing or changing it makes stored LinkedIn tokens unusable. Token refresh is not implemented; reconnect after token expiry.

To turn typed or transcribed interview notes into a humanized post draft, configure `GEMINI_API_KEY` or `GROQ_API_KEY` on the service and select the matching provider in Settings. The source notes are sent to that provider. AI-generated content remains a draft and still requires your review and explicit approval. Post images are stored in PostgreSQL and uploaded through LinkedIn's Images API when the approved post is published.

If publishing appears stuck, check the post status in Content Studio and confirm LinkedIn still shows **Connected**. Approval schedules the post for the next configured daily slot; in this deployment the GitHub Actions scheduler triggers at 03:30 UTC (09:00 Asia/Kolkata). Confirm the workflow has run successfully and that the GitHub `SCHEDULER_TRIGGER_TOKEN` matches the Render service; set `APP_URL` only when overriding the default service URL. Posts over 15 minutes late are held for manual review. A failed publishing attempt is not automatically retried; verify the LinkedIn feed before taking further action.

## Local Docker deployment

1. Install Docker Desktop and create a private `.env` from `.env.example`.
2. Set `APP_ADMIN_PASSWORD`, `APP_SESSION_SECRET`, and, if connecting LinkedIn, the OAuth and encryption values above.
3. Start the app from the repository root:

   ```powershell
   docker compose up --build -d
   ```

4. Open `http://localhost:8000`. Docker Compose stores local SQLite data in the persistent `brand_agent_data` volume.

## Reliability limitations

- The free Render service may sleep; the first scheduler request can be delayed while it wakes.
- GitHub Actions schedules are best effort and may start later than requested.
- A run delayed by more than 15 minutes marks a scheduled post for review; the app does not silently catch up.
- Back up the PostgreSQL database and keep the LinkedIn encryption key secure.
- Free-tier availability, quotas, and provider terms can change. Check current provider terms before relying on this setup.

Never paste passwords, database URLs, API keys, or OAuth tokens into chat or commit them to Git.
