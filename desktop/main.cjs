const { app, BrowserWindow, Menu, nativeImage, Notification, shell, Tray } = require('electron');
const { shouldSendReminder } = require('./reminder-policy.cjs');

const APP_URL = process.env.BRAND_AGENT_URL || 'https://linkedin-ai-publisher.onrender.com';
const POLL_INTERVAL_MS = 60_000;

let mainWindow;
let tray;
let pollTimer;
let lastReminderAt = 0;
let remindersEnabledAtLogin = false;
let launchedAtLogin = false;
let reminderCheckInProgress = false;

const hasSingleInstanceLock = app.requestSingleInstanceLock();
if (!hasSingleInstanceLock) {
  app.quit();
}

app.on('second-instance', showWindow);

if (process.platform === 'win32') {
  app.setAppUserModelId('com.tilak623.personalbrandingagent');
}

function isAllowedAppUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'https:' ||
      (url.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(url.hostname));
  } catch {
    return false;
  }
}

function showWindow() {
  if (!mainWindow) {
    createWindow();
  }
  mainWindow.show();
  mainWindow.focus();
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      partition: 'persist:brand-agent',
    },
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('https://')) {
      void shell.openExternal(url);
    }
    return { action: 'deny' };
  });
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (new URL(url).origin !== new URL(APP_URL).origin) {
      event.preventDefault();
      if (url.startsWith('https://')) {
        void shell.openExternal(url);
      }
    }
  });
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
  mainWindow.once('ready-to-show', () => {
    if (!launchedAtLogin) {
      mainWindow.show();
    }
    void checkReminderStatus();
  });
  mainWindow.webContents.on('did-finish-load', () => {
    void checkReminderStatus();
  });
  void mainWindow.loadURL(APP_URL);
}

async function readWebsiteState() {
  if (!mainWindow || mainWindow.webContents.isDestroyed() || mainWindow.webContents.isLoading()) {
    return null;
  }

  return mainWindow.webContents.executeJavaScript(`(async () => {
    const requestOptions = {
      credentials: 'include',
      signal: AbortSignal.timeout(10000),
    };
    const auth = await fetch('/api/v1/auth/me', requestOptions);
    if (!auth.ok) return { authenticated: false };
    const authBody = await auth.json();
    if (!authBody.data || !authBody.data.authenticated) return { authenticated: false };
    const [settingsResponse, interviewResponse] = await Promise.all([
      fetch('/api/v1/settings', requestOptions),
      fetch('/api/v1/interviews/today', requestOptions),
    ]);
    if (!settingsResponse.ok || !interviewResponse.ok) {
      throw new Error('The website could not load reminder settings.');
    }
    const [settingsBody, interviewBody] = await Promise.all([
      settingsResponse.json(),
      interviewResponse.json(),
    ]);
    return {
      authenticated: true,
      remindersEnabled: Boolean(settingsBody.data && settingsBody.data.reminders_enabled),
      intervalMins: Number(settingsBody.data && settingsBody.data.reminder_interval_mins),
      interviewCompleted: Boolean(interviewBody.data && interviewBody.data.completed),
    };
  })()`);
}

async function checkReminderStatus() {
  if (reminderCheckInProgress) {
    return;
  }
  reminderCheckInProgress = true;
  try {
    const state = await readWebsiteState();
    const now = Date.now();
    if (!shouldSendReminder(state, lastReminderAt, now)) {
      return;
    }
    if (!Notification.isSupported()) {
      throw new Error('Windows notifications are not available on this device.');
    }
    const reminder = new Notification({
      title: 'Daily interview reminder',
      body: 'Take a few minutes to reflect on what you worked on or learned today.',
    });
    reminder.on('click', showWindow);
    reminder.show();
    lastReminderAt = now;
  } catch (error) {
    console.error('Interview reminder check failed:', error);
  } finally {
    reminderCheckInProgress = false;
  }
}

function createTray() {
  const svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><rect width="16" height="16" rx="3" fill="#6366f1"/><path d="M4 4h8v2H6v2h5v2H6v2H4z" fill="#fff"/></svg>';
  const icon = nativeImage.createFromDataURL(
    `data:image/svg+xml;base64,${Buffer.from(svgIcon).toString('base64')}`,
  );
  tray = new Tray(icon);
  tray.setToolTip('Personal Branding Agent');
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Open Personal Branding Agent', click: showWindow },
    { label: 'Check reminder now', click: () => { lastReminderAt = 0; void checkReminderStatus(); } },
    { type: 'separator' },
    {
      label: 'Start at Windows sign-in',
      type: 'checkbox',
      checked: remindersEnabledAtLogin,
      click: (item) => {
        remindersEnabledAtLogin = item.checked;
        app.setLoginItemSettings({ openAtLogin: item.checked });
      },
    },
    { type: 'separator' },
    { label: 'Quit', click: () => { app.isQuitting = true; app.quit(); } },
  ]));
  tray.on('double-click', showWindow);
}

if (!isAllowedAppUrl(APP_URL)) {
  throw new Error('BRAND_AGENT_URL must use HTTPS or a localhost HTTP URL.');
}

app.whenReady().then(() => {
  if (!hasSingleInstanceLock) {
    return;
  }
  const loginSettings = app.getLoginItemSettings();
  remindersEnabledAtLogin = loginSettings.openAtLogin;
  launchedAtLogin = loginSettings.wasOpenedAtLogin;
  createTray();
  createWindow();
  pollTimer = setInterval(() => { void checkReminderStatus(); }, POLL_INTERVAL_MS);
});

app.on('before-quit', () => {
  if (pollTimer) clearInterval(pollTimer);
  app.isQuitting = true;
});
