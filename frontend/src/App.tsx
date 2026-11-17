import React, { useState, useEffect } from 'react';
import { WorkspaceView, HealthResponse, UserAuthStatus, UserSettings } from './types';
import { api } from './services/api';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Home } from './pages/Home';
import { Interview } from './pages/Interview';
import { ContentStudio } from './pages/ContentStudio';
import { MediaStudio } from './pages/MediaStudio';
import { Calendar } from './pages/Calendar';
import { Research } from './pages/Research';
import { Memory } from './pages/Memory';
import { Portfolio } from './pages/Portfolio';
import { Networking } from './pages/Networking';
import { Analytics } from './pages/Analytics';
import { Profile } from './pages/Profile';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<WorkspaceView>('home');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [authStatus, setAuthStatus] = useState<UserAuthStatus | null>(null);
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const [healthRes, authRes, settingsRes] = await Promise.all([
        api.getHealth(),
        api.getAuthStatus(),
        api.getSettings(),
      ]);

      if (healthRes.success && healthRes.data) {
        setHealth(healthRes.data);
      }
      if (authRes.success && authRes.data) {
        setAuthStatus(authRes.data);
        if (!authRes.data.onboarding_completed) {
          setCurrentView('profile');
        }
      }
      if (settingsRes.success && settingsRes.data) {
        setSettings(settingsRes.data);
        if (settingsRes.data.theme === 'light' || settingsRes.data.theme === 'dark') {
          setTheme(settingsRes.data.theme);
        }
      }
      setLoading(false);
    };

    fetchData();

    // Periodic health poll every 20 seconds
    const interval = setInterval(async () => {
      const res = await api.getHealth();
      if (res.success && res.data) {
        setHealth(res.data);
      }
    }, 20000);

    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    if (next === 'light') {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    }
  };

  const handleLogout = async () => {
    await api.logout();
    setAuthStatus(null);
  };

  if (!loading && !authStatus?.authenticated) {
    return <Login onAuthenticated={() => window.location.reload()} />;
  }

  return (
    <div className={`min-h-screen flex ${theme === 'dark' ? 'dark bg-surface-950 text-slate-100' : 'light bg-slate-50 text-slate-900'}`}>
      <Sidebar currentView={currentView} onNavigate={setCurrentView} />

      <div className="flex-1 flex flex-col min-w-0">
        <Header
          currentView={currentView}
          onNavigate={setCurrentView}
          health={health}
          authStatus={authStatus}
          loading={loading}
          theme={theme}
          onToggleTheme={toggleTheme}
          onLogout={handleLogout}
        />

        <main className="flex-1 p-6 overflow-y-auto">
          {currentView === 'home' && <Home onNavigate={setCurrentView} health={health} authStatus={authStatus} />}
          {currentView === 'interview' && <Interview />}
          {currentView === 'content' && <ContentStudio />}
          {currentView === 'media' && <MediaStudio />}
          {currentView === 'calendar' && <Calendar />}
          {currentView === 'research' && <Research />}
          {currentView === 'memory' && <Memory />}
          {currentView === 'portfolio' && <Portfolio />}
          {currentView === 'networking' && <Networking />}
          {currentView === 'analytics' && <Analytics />}
          {currentView === 'profile' && (
            <Profile
              onOnboardingComplete={(fullName) => setAuthStatus((current) => current
                ? { ...current, full_name: fullName, onboarding_completed: true }
                : current)}
            />
          )}
          {currentView === 'settings' && (
            <Settings
              settings={settings}
              onSettingsUpdated={setSettings}
              theme={theme}
              onToggleTheme={toggleTheme}
            />
          )}
        </main>
      </div>
    </div>
  );
};
