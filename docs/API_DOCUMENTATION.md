# REST API Documentation

Base URL: `http://localhost:8000/api/v1`

> **Implementation status:** The foundation and Phase 2 profile/memory endpoints described below are implemented. The later-module routes in this document are planned API contracts and are not available yet.

All responses are formatted in JSON with standardized envelope schemas:
```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2026-11-16T18:00:00Z"
}
```

---

## 1. System & Health

### `GET /health`
Returns the local backend/database status and host resource information.

### `GET /auth/me`
Returns the current local profile summary and whether first-run onboarding has been completed. Authentication is not implemented; this is a single-user local application.

### `GET /system/resources`
Planned. Resource information is currently included in `GET /health`.

---

## 2. Onboarding & Professional Memory

### `POST /profile/onboard`
Creates or updates the local professional profile and can save initial skills.
- **Request Body**:
  ```json
  {
    "full_name": "Developer Name",
    "headline": "Full-Stack & AI Systems Engineer",
    "career_direction": "Building high-performance AI tools",
    "target_audience": "Tech leads, senior engineers, founders",
    "github_username": "dev-username",
    "initial_skills": [
      {"name": "Python", "proficiency_level": "implemented"},
      {"name": "FastAPI", "proficiency_level": "implemented"},
      {"name": "LangChain", "proficiency_level": "studied"}
    ]
  }
  ```

### `GET /profile`
Retrieves the local professional profile.

### `/memory/skills`
- `GET /memory/skills` lists saved skills.
- `POST /memory/skills` creates a skill with proficiency level (`implemented`, `studied`, `explored`, or `discovered`).
- `PATCH /memory/skills/{id}` updates a skill.
- `DELETE /memory/skills/{id}` deletes a skill.

### `/memory/projects`
- `GET /memory/projects` lists saved projects.
- `POST /memory/projects` creates a project.
- `PATCH /memory/projects/{id}` updates a project.
- `DELETE /memory/projects/{id}` deletes a project.

### `/memory/milestones`
- `GET /memory/milestones` lists learning milestones.
- `POST /memory/milestones` creates a milestone.
- `PATCH /memory/milestones/{id}` updates a milestone.
- `DELETE /memory/milestones/{id}` deletes a milestone.

### `GET /memory/search?q={query}`
Searches profile, skill, project, and learning-milestone text using the local SQLite full-text index.

### `GET /memory/export`
Exports the local profile, skills, projects, and learning milestones as JSON.

---

## 3. AI Interviewer

### `POST /interviews/start`
Starts a new daily interview session.
- **Request Body**:
  ```json
  {
    "mode": "voice" // or "text"
  }
  ```
- **Response**:
  ```json
  {
    "interview_id": "uuid",
    "question": "Hey! What was the most interesting programming puzzle or concept you tackled today?",
    "turn_number": 1
  }
  ```

### `POST /interviews/{id}/turn`
Submits user answer and returns adaptive follow-up or completion signal.
- **Request Body**:
  ```json
  {
    "user_response": "I refactored our caching layer using Redis pipelining and reduced latency by 35%."
  }
  ```
- **Response**:
  ```json
  {
    "analysis": {
      "category": "technical_milestone",
      "extracted_skills": ["Redis", "Caching", "Performance Optimization"],
      "proficiency": "implemented"
    },
    "is_completed": false,
    "next_question": "That's a significant drop! What were the unexpected edge cases you ran into with TTLs?"
  }
  ```

### `POST /interviews/{id}/complete`
Manually concludes an interview and triggers automatic synthesis of draft posts and memory entries.

---

## 4. Technology Research Engine

### `GET /research/daily`
Fetches verified daily tech trends across Hacker News, ArXiv, Reddit, and GitHub.
- **Query Params**: `category=ai_ml&min_credibility=0.7`

### `POST /research/refresh`
Triggers an immediate asynchronous background scan of authorized research sources.

---

## 5. Content Creation Studio

### `POST /content/generate`
Generates 2–3 draft LinkedIn posts from recent interviews, project updates, or research items.
- **Request Body**:
  ```json
  {
    "source_type": "interview",
    "source_id": "uuid",
    "tone": "direct_technical",
    "format": "technical_breakdown"
  }
  ```

### `PUT /content/{id}`
Updates draft text, hashtags, or formatting.

### `POST /content/{id}/fact-check`
Runs an anti-hallucination and claim-verification pass against user memory and GitHub evidence.

### `POST /content/{id}/approve`
**MANDATORY USER ACTION**: Records user approval with timestamp before publishing or scheduling.

---

## 6. Media Generation Studio

### `POST /media/generate-infographic`
Generates a crisp SVG / PNG technical card or code snippet.
- **Request Body**:
  ```json
  {
    "template": "code_snippet_dark",
    "code": "def optimize(): pass",
    "language": "python",
    "title": "Redis Pipelining Explained"
  }
  ```

### `POST /media/generate-carousel`
Generates a multi-slide PDF/PNG carousel for LinkedIn document posts.

---

## 7. LinkedIn Publishing & Fallbacks

### `POST /linkedin/publish`
Publishes an approved post using the official `w_member_social` API endpoint.
- **Precondition**: `status == 'approved'`.

### `POST /linkedin/manual-prepare`
Prepares formatted text, media, and hashtags for one-click manual pasting when direct API is unavailable.

---

## 8. Windows Desktop Companion & Reminders

### `GET /desktop/status`
Returns reminder schedule, idle timer, and background notification status.

### `POST /desktop/reminders/pause`
Pauses 15-minute reminders for a specified duration (e.g., 60 minutes) or until tomorrow.

### `POST /desktop/reminders/resume`
Resumes 15-minute reminder schedule.

### `POST /desktop/scan-folder`
Scans an authorized local directory in read-only mode for markdown notes, architecture diagrams, or code.
