# Windows Desktop Companion

The companion runs in the Windows system tray and sends interview reminders using the settings saved by the website. It does not contain API keys or store the website password.

## Run from source

1. Install Node.js 18 or newer.
2. From PowerShell, open the repository's `desktop` folder and install dependencies:

   ```powershell
   Set-Location desktop
   npm.cmd install
   ```

3. Start the companion:

   ```powershell
   npm.cmd start
   ```

   By default, it opens `https://linkedin-ai-publisher.onrender.com`. To use a local development website instead, set the URL before starting:

   ```powershell
   $env:BRAND_AGENT_URL = "http://localhost:5173"
   npm.cmd start
   ```

4. Sign in to the website inside the companion window. The companion uses that signed-in session to read reminder settings and today's interview status.
5. In the website's **Settings**, enable reminders and choose 15, 30, or 60 minutes. The companion checks for an unfinished interview and stops notifying when today's interview is complete.
6. Use the tray icon's menu to check a reminder immediately or enable **Start at Windows sign-in**. Closing the window hides the app to the tray; choose **Quit** to stop reminders.

The companion must be running, signed in, and able to reach the website. Notifications also depend on Windows notification settings. The companion does not run when the PC is shut down or asleep.

## Build a Windows installer

From the `desktop` folder:

```powershell
npm.cmd run dist
```

The installer is written to `desktop\release`. Install it on the Windows computer where reminders should appear.
