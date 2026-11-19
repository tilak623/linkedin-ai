# Troubleshooting & Diagnostic Guide

## 1. Common Issues & Solutions

### 1.1 PowerShell Execution Policy Blocks `npm.ps1`
- **Symptom**: `npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system.`
- **Cause**: Windows PowerShell default script execution policy prevents running unsigned `.ps1` wrapper scripts.
- **Solution**:
  - Run `npm.cmd` instead of `npm` (e.g., `npm.cmd install`, `npm.cmd run dev`).
  - Or run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

### 1.2 Free AI API Rate Limits (429 Too Many Requests)
- **Symptom**: Cloud AI requests fail with HTTP 429.
- **Cause**: Exceeded Gemini or Groq free tier requests per minute (RPM).
- **Solution**:
  - Humanized post drafts use the provider selected in Settings and do not silently switch providers. Wait and retry, or select a different provider that has an API key configured.
  - Offline mode disables external AI drafting; turn it off before generating a humanized post.

### 1.3 Web Speech API Not Hearing Microphone
- **Symptom**: Voice interview button does not pick up voice or fails immediately.
- **Cause**: Browser microphone permissions blocked or OS privacy settings restricting microphone access.
- **Solution**:
  - Check browser permissions icon in the address bar and allow microphone.
  - In Windows Settings, verify **Privacy & Security > Microphone > Let desktop apps access your microphone** is enabled.
  - Click the **Switch to Text Mode** toggle to continue typing without voice interruption.

### 1.4 Supabase Connection Failed (Offline Mode)
- **Symptom**: App indicates `Cloud Database Unreachable`.
- **Cause**: No internet connection or invalid Supabase URL/Key.
- **Solution**:
  - The application automatically switches to local embedded SQLite (`brand_agent.db`).
  - All your actions are staged in `sync_queue` and will sync once connectivity returns.

### 1.5 Desktop Notification Not Popping Up
- **Symptom**: 15-minute interview reminder does not show on Windows desktop.
- **Cause**: Windows "Focus Assist" / "Do Not Disturb" is turned on.
- **Solution**:
  - Check Windows notification center and turn off "Do Not Disturb".
  - Ensure notifications are enabled for Electron in Windows Settings > System > Notifications.

### 1.6 LinkedIn Post Not Publishing
- **Symptom**: An approved post remains scheduled or changes to **Missed schedule** or **Publishing failed**.
- **Cause**: Approval schedules for the next daily posting slot; publishing requires an active LinkedIn connection and a successful scheduler run.
- **Solution**:
  - In Content Studio, check the LinkedIn connection, post status, and displayed schedule time.
  - For Render, confirm the GitHub Actions scheduler workflow ran and its `APP_URL` and `SCHEDULER_TRIGGER_TOKEN` secrets match the service configuration.
  - Reconnect LinkedIn if its token expired. Posts held for a missed schedule need a new explicit approval.
  - For **Publishing failed**, check the LinkedIn feed before retrying; the app prevents automatic retries to avoid duplicate posts.
