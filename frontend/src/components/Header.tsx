import React from 'react';
import { Sun, Moon, Sparkles, Bell } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import { HealthResponse, UserAuthStatus, WorkspaceView } from '../types';

interface HeaderProps {
  currentView: WorkspaceView;
  onNavigate: (view: WorkspaceView) => void;
  health: HealthResponse | null;
  authStatus: UserAuthStatus | null;
  loading: boolean;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

const VIEW_TITLES: Record<WorkspaceView, { title: string; subtitle: string }> = {
  home: { title: 'Executive Command Center', subtitle: 'Personal branding overview, daily standup, and intelligence' },
  interview: { title: 'AI Daily Interviewer', subtitle: 'Voice and text reflection to capture daily engineering progress' },
  content: { title: 'AI Content Studio', subtitle: 'Authentic LinkedIn post crafting with human review & anti-cliché filters' },
  media: { title: 'Media Generation Studio', subtitle: 'Programmatic infographics, technical architecture diagrams, & carousels' },
  calendar: { title: 'Smart Content Calendar', subtitle: 'Strategic publication scheduling and cadence optimization' },
  research: { title: 'Technology Research Engine', subtitle: 'Verified daily discoveries from Hacker News, ArXiv, Reddit, & GitHub' },
  memory: { title: 'Professional Memory Library', subtitle: 'Searchable skills, evidence notes, and hierarchical experience' },
  portfolio: { title: 'Portfolio & GitHub Intelligence', subtitle: 'Real repository analysis without exaggeration' },
  networking: { title: 'Professional Networking Assistant', subtitle: 'Meaningful connection requests and discussion opportunities' },
  analytics: { title: 'LinkedIn Analytics Dashboard', subtitle: 'Genuine engagement metrics and performance intelligence' },
  profile: { title: 'Profile Optimization Manager', subtitle: 'Headline, summary, and positioning recommendations' },
  settings: { title: 'Settings & Privacy Centre', subtitle: 'Local permissions, reminder controls, and complete data ownership' },
};

export const Header: React.FC<HeaderProps> = ({
  currentView,
  onNavigate,
  health,
  authStatus,
  loading,
  theme,
  onToggleTheme,
}) => {
  const { title, subtitle } = VIEW_TITLES[currentView] || { title: 'Workspace', subtitle: '' };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 border-b border-surface-800 bg-surface-950/80 backdrop-blur-md">
      <div>
        <h1 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
          {title}
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        <StatusBadge health={health} loading={loading} />

        {currentView !== 'interview' && (
          <button
            onClick={() => onNavigate('interview')}
            className="hidden md:flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-brand-600 hover:bg-brand-500 text-white transition-all shadow-sm shadow-brand-500/20"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Daily Interview</span>
          </button>
        )}

        <button
          onClick={onToggleTheme}
          aria-label="Toggle Theme"
          className="p-2 rounded-lg bg-surface-800 hover:bg-surface-800/80 text-slate-300 hover:text-white border border-slate-700/50 transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
        </button>

        {authStatus && (
          <div className="flex items-center gap-3 pl-2 border-l border-surface-800">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-xs font-bold text-white shadow-inner">
              {authStatus.full_name ? authStatus.full_name[0] : 'U'}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
