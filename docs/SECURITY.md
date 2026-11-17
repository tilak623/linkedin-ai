# Security Policy & Architecture

> **Status:** This document states security requirements for the product. They are not all implemented yet; in particular, the current local app does not have user authentication, cloud RLS, or an Electron/local-folder scanner.

## 1. Security Architecture Principles

The **Personal Branding AI Agent** enforces defense-in-depth principles across client, API, AI, and storage tiers.

---

## 2. Credential & Key Management
- **Zero Secrets Committed**: `.env`, `.env.local`, API keys, OAuth tokens, and secrets are strictly excluded by `.gitignore`.
- **Environment Isolation**: Production tokens are injected strictly via OS environment variables.
- **Client Sanitization**: Frontend bundles and client logs never contain API secrets or service-role keys. Only public `anon` keys and authenticated session JWTs are shared with the client.

---

## 3. Local File System Access Controls
- **Explicit Authorization**: The backend and Electron app never perform unprompted recursive scans of the user's hard drive.
- **Read-Only Inspection**: All local project parsing functions open files strictly in read-only mode (`r` / `rb`).
- **Deny-by-Default File Filters**: The scanning engine automatically skips and ignores:
  - Private credential files (`.env*`, `id_rsa`, `*.pem`, `*.key`, `credentials.json`)
  - Hidden source control folders (`.git`, `.svn`)
  - Build and binary directories (`node_modules`, `venv`, `dist`, `build`, `__pycache__`)
  - System directories (`C:\Windows`, `C:\Program Files`)
- **Permission Checkpoint**: Before sending any extracted local technical text to external AI models, the UI asks the user for explicit confirmation.

---

## 4. Human-in-the-Loop Public Action Boundary
- **Zero Autonomous Publishing**: Under no circumstances does the AI publish posts, post comments, or send connection requests autonomously.
- **Mandatory Approval State**: A post cannot transition to `published` status without an explicit approval log record signed by user interaction.
- **Anti-Spam Controls**: Connection request suggestions and networking drafts include rate-limiting and anti-spam verifications to preserve user reputation.

---

## 5. Multi-User Isolation
- When expanded beyond personal use, all database tables implement Supabase Row Level Security (RLS) guaranteeing that `user_id = auth.uid()`.
- Data leaking across user boundaries is prevented at the database kernel level.
