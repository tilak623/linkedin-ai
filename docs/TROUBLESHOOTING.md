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
  - The AI Provider Manager automatically falls back to secondary free providers (e.g., Gemini -> Groq -> Local SLM).
  - You can also enable `Offline / Local Model` mode in Settings.

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
