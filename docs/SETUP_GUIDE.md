# Setup and Installation Guide

## 1. Prerequisites

Ensure the following tools are installed on your Windows machine:
- **Python**: Version 3.11+ (verified: Python 3.13.7 64-bit installed).
- **Node.js**: Version 18+ (verified: Node v24.15.0 installed).
- **Git**: Installed and available in PATH.
- **npm**: Note that on Windows PowerShell, run `npm.cmd` if PowerShell scripts (`.ps1`) are restricted by system execution policy.

---

## 2. Environment Variables Configuration

The current Phase 2 onboarding and memory features do not require AI or Supabase credentials. Configure these only when the corresponding integrations are implemented.

Create a `.env` file in the root directory (or in `backend/.env`):

```env
# Application Settings
ENVIRONMENT=development
PORT=8000
HOST=127.0.0.1
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Database Connection (Supabase Cloud Free Tier)
# If left blank, the application will automatically fall back to local SQLite!
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=sqlite+aiosqlite:///./brand_agent.db

# Zero-Cost Free AI Providers (Get free keys with zero billing)
# 1. Google AI Studio (Free Gemini API): https://aistudio.google.com/
GEMINI_API_KEY=your_free_gemini_api_key

# 2. Groq Cloud (Free high-speed inference): https://console.groq.com/
GROQ_API_KEY=your_free_groq_api_key

# Optional: LinkedIn Developer App (for direct API publishing)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/linkedin/callback
```

---

## 3. Step-by-Step Setup

### Step 3.1 Backend Setup
Open a terminal in the project root:
```powershell
cd backend

# Create Python virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Run backend development server
python run.py
```
Backend API will be live at `http://localhost:8000`.  
Swagger interactive API docs will be at `http://localhost:8000/docs`.

### Step 3.2 Frontend Setup
Open a second terminal:
```powershell
cd frontend

# Install node dependencies
npm.cmd install

# Start Vite React development server
npm.cmd run dev
```
Web Workspace will be live at `http://localhost:5173`.

The Electron desktop companion is a future phase and is not included in the current repository.

---

## 4. Verification Checklist
- [x] Backend responds to `GET http://localhost:8000/api/v1/health`.
- [x] Frontend opens in browser at `http://localhost:5173`.
- [x] Web Speech API microphone permission allowed for voice interviews.
- [x] Windows notification pops up for interview reminder.
