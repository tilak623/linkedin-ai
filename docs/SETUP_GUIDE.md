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

LinkedIn posting needs your own Developer app with `openid`, `profile`, and `w_member_social` access. Configure its HTTPS callback to exactly match `LINKEDIN_REDIRECT_URI`; see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md). Keep all client credentials in environment variables or the host's secret manager. The OAuth-authorized member must be the account you intend to post from.

The local draft generator uses saved interview, project, or learning notes. It does not call an AI model and will not invent personal claims. Every public post requires your explicit approval.

## Local verification

```powershell
python -m unittest discover -s backend\tests -v
Set-Location frontend
npm.cmd run build
```
