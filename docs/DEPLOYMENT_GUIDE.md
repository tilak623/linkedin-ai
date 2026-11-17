# Deployment Guide (Strictly Free Architecture)

This guide documents how to deploy the **Personal Branding AI Agent** to free cloud hosting platforms with zero recurring cost.

---

## 1. Cloud Architecture Overview

| Component | Free Platform | Free Tier Quota | Role |
| :--- | :--- | :--- | :--- |
| **Database & Auth** | Supabase | 500 MB Postgres, 1 GB Storage, 50k MAU | Primary cloud database, user auth, RLS |
| **Backend API** | Render / Railway / Koyeb | Free Web Service tier (512 MB RAM, free spin-down) | FastAPI REST API Gateway |
| **Web Frontend** | Vercel / Netlify | Unlimited personal projects, 100 GB bandwidth | React + TypeScript SPA |
| **Desktop Companion** | Local Windows Installation | Native Electron desktop binary | Background reminders, tray icon, local files |

---

## 2. Supabase Configuration (Free Tier)

1. Create a free project at [supabase.com](https://supabase.com).
2. Navigate to **SQL Editor** in your Supabase dashboard.
3. Paste and run the schema defined in `docs/DATABASE_SCHEMA.md`.
4. Copy the following credentials from **Project Settings > API**:
   - `Project URL` -> `SUPABASE_URL`
   - `anon public key` -> `SUPABASE_ANON_KEY`
   - `service_role secret` -> `SUPABASE_SERVICE_ROLE_KEY`

---

## 3. Frontend Deployment (Vercel / Netlify)

1. Push your repository to GitHub.
2. Link the repository to [Vercel](https://vercel.com) or [Netlify](https://netlify.com).
3. Set the root directory to `frontend`.
4. Set the build command to `npm run build` and output directory to `dist`.
5. Set environment variable:
   - `VITE_API_URL=https://your-backend-api.onrender.com/api/v1`
   - `VITE_SUPABASE_URL=https://your-project.supabase.co`
   - `VITE_SUPABASE_ANON_KEY=your-anon-key`

---

## 4. Backend Deployment (Render Free Web Service)

1. Connect your repository to [Render](https://render.com).
2. Choose **Web Service** with runtime `Python 3`.
3. Set root directory to `backend`.
4. Build command: `pip install -r requirements.txt`.
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add environment variables:
   - `ENVIRONMENT=production`
   - `SUPABASE_URL=https://your-project.supabase.co`
   - `SUPABASE_ANON_KEY=your-anon-key`
   - `SUPABASE_SERVICE_ROLE_KEY=your-service-key`
   - `GEMINI_API_KEY=your-gemini-key`
   - `GROQ_API_KEY=your-groq-key`
   - `CORS_ORIGINS=["https://your-frontend.vercel.app"]`

---

## 5. Offline & Hybrid Synchronization
- The Windows Desktop companion runs locally and maintains an embedded `brand_agent.db` SQLite database.
- When an internet connection is active, changes staged in `sync_queue` automatically synchronize to Supabase via idempotent batch updates.
- If cloud services are unreachable or free quotas are exceeded, the app continues operating smoothly in local mode.
