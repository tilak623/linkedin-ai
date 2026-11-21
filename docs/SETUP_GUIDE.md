# Setup and Installation Guide

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- Git
- PowerShell on Windows

## Local development

From the repository root, install the backend packages and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python backend\run.py
```

In another terminal:

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`. Vite proxies `/api` requests to `http://127.0.0.1:8000`. Local development binds the API to loopback and uses SQLite; external provider keys are not needed for the profile, interview, and evidence-based draft features.

## LinkedIn integration

To connect your account:

1. Sign in to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps) with the LinkedIn account you intend to connect and create an app. LinkedIn may require a company page and verification before it will let you create or enable products.
2. Open the app's **Products** tab and request/enable **Sign In with LinkedIn using OpenID Connect** and **Share on LinkedIn**. The app needs `openid`, `profile`, and `w_member_social`. LinkedIn must approve the product access; creating an app alone does not grant publishing access.
3. In **Auth**, copy the **Client ID** and **Client Secret**. Add the exact OAuth redirect URL:
   - Local development: `http://localhost:8000/api/v1/linkedin/callback`
   - Hosted site: `https://YOUR-HOST/api/v1/linkedin/callback`
   The redirect URL registered in LinkedIn must exactly match `LINKEDIN_REDIRECT_URI`.
4. Put the credentials in the backend environment, never in the frontend or chat:
   - For local PowerShell, set `$env:LINKEDIN_CLIENT_ID`, `$env:LINKEDIN_CLIENT_SECRET`, and `$env:LINKEDIN_TOKEN_ENCRYPTION_KEY` in the same terminal before starting `python backend\run.py`. Generate an encryption key with the command in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md). Keep this key stable so saved tokens remain decryptable.
   - For Render, add the three values under the service's **Environment** settings. See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for the production callback and exact deployment steps.
5. Start the website, open **Content Studio → Connect LinkedIn**, and complete LinkedIn's consent screen. Confirm the displayed member is your intended account. A post is not published until you review and approve that exact post.

The local draft generator uses saved interview, project, or learning notes. It does not call an AI model and will not invent personal claims. Every public post requires your explicit approval.

## Zero-cost AI provider setup

The interview flow can send your notes to Gemini or Groq to create an editable draft. Both are external services; free-tier availability, quotas, and terms may change. Notes you submit are sent to the provider you select. Deterministic evidence-based drafts do not require an AI key.

1. Choose one provider and create an API key from its official developer console: [Google AI Studio](https://aistudio.google.com/apikey) for Gemini, or [Groq Console](https://console.groq.com/keys) for Groq.
2. For local development, set the matching variable in the same PowerShell terminal that starts the backend:

   ```powershell
   $env:GEMINI_API_KEY = "paste-your-key-here"
   # Or, instead:
   $env:GROQ_API_KEY = "paste-your-key-here"
   python backend\run.py
   ```

   Do not add a real key to `.env.example`, frontend code, or a committed file. If you use Docker Compose, put the variable in your private root `.env` file (created from `.env.example`) instead.
3. For Render, open your service's **Environment** settings, add `GEMINI_API_KEY` or `GROQ_API_KEY` with the key as its value, save, and redeploy/restart the service.
4. In the website, open **Settings → Zero-Cost AI Engine Provider**, select the provider whose key you added, and save settings. The card reports whether the backend sees a key; it never displays the key itself.
5. In **Interview**, use **Create a humanized LinkedIn draft**. The result remains a draft for you to edit and approve. The Local SLM option is not implemented yet.

## Local verification

```powershell
python -m unittest discover -s backend\tests -v
Set-Location frontend
npm.cmd run build
```
