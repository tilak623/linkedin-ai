# Testing & Quality Assurance Strategy

## 1. Testing Philosophy

Testing is mandatory for every module. A module is not complete simply because its UI renders without errors; its underlying business logic, state transitions, security boundaries, and data persistence must be formally validated.

---

## 2. Test Pyramid & Categories

```
       /\
      /  \     End-to-End & Desktop Tests (Playwright / Electron tests)
     /----\
    /      \   Integration & API Tests (FastAPI TestClient + Database tests)
   /--------\
  /          \ Unit Tests (AI prompt parsers, memory logic, media generators)
 /------------\
```

### 2.1 Backend Unit & Integration Tests (pytest)
- **Memory Service Tests**: Ensure proficiency level transitions (`discovered` -> `explored` -> `studied` -> `implemented`) validate correctly.
- **Interviewer Logic Tests**: Ensure interview turns evaluate completion triggers and do not enter endless loops.
- **Content Studio Tests**: Ensure anti-cliché filters reject forbidden buzzwords and enforce human tone requirements.
- **Media Engine Tests**: Validate that PNG/SVG generators output valid files with correct dimensions.
- **LinkedIn Publisher Tests**: Ensure posts cannot be published without explicit approval status (`status == 'approved'`).
- **Database Isolation Tests**: Ensure RLS and user ID filters prevent cross-user data access.

### 2.2 Frontend Unit & Component Tests (Vitest + React Testing Library)
- **Workspace Navigation**: Verify all 12 page routes load correctly.
- **Approval Checkpoint**: Verify the "Approve Post" modal blocks publishing until user confirms.
- **Web Speech Hook**: Test fallback to text input when microphone permissions are denied.
- **Theme Switcher**: Ensure theme state switches cleanly between light and dark modes.

### 2.3 Desktop & Reminder Tests
- **Notification Timer**: Verify 15-minute reminder loop pauses, resumes, and stops upon interview completion.
- **Local Scanner**: Test that `.env` and credential files are automatically filtered out during folder parsing.

---

## 3. How to Execute Tests

### Run All Backend Tests
```powershell
cd backend
python -m pytest tests/ -v
```

### Run Tests with Coverage
```powershell
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Run Frontend Tests
```powershell
cd frontend
npm.cmd test
```
