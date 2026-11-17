import React from 'react';
import {
  LayoutDashboard,
  Mic,
  PenTool,
  Image,
  Calendar,
  Compass,
  Brain,
  FolderGit2,
  Users,
  BarChart3,
  UserCheck,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { WorkspaceView } from '../types';

interface SidebarProps {
  currentView: WorkspaceView;
  onNavigate: (view: WorkspaceView) => void;
}

interface NavItem {
  id: WorkspaceView;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
  phase: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'home', label: 'Command Center', icon: LayoutDashboard, phase: 'Phase 1' },
  { id: 'interview', label: 'Daily Interview', icon: Mic, badge: 'Daily', phase: 'Phase 3' },
  { id: 'content', label: 'Content Studio', icon: PenTool, phase: 'Phase 5' },
  { id: 'media', label: 'Media Studio', icon: Image, phase: 'Phase 6' },
  { id: 'calendar', label: 'Content Calendar', icon: Calendar, phase: 'Phase 9' },
  { id: 'research', label: 'Tech Research', icon: Compass, phase: 'Phase 4' },
  { id: 'memory', label: 'Professional Memory', icon: Brain, phase: 'Phase 2' },
  { id: 'portfolio', label: 'Portfolio & GitHub', icon: FolderGit2, phase: 'Phase 7' },
  { id: 'networking', label: 'Networking', icon: Users, phase: 'Phase 10' },
  { id: 'analytics', label: 'Analytics', icon: BarChart3, phase: 'Phase 9' },
  { id: 'profile', label: 'Profile Manager', icon: UserCheck, phase: 'Phase 10' },
  { id: 'settings', label: 'Settings & Privacy', icon: ShieldCheck, phase: 'Phase 1' },
];

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate }) => {
  return (
    <aside className="w-64 border-r border-surface-800 bg-surface-950 flex flex-col justify-between h-screen sticky top-0 shrink-0">
      <div>
        {/* App Logo & Brand Identity */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-surface-800/80">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="font-semibold text-sm tracking-tight text-slate-100 flex items-center gap-1.5">
              <span>Antigravity</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 font-medium">AI</span>
            </div>
            <div className="text-[11px] text-slate-400">Personal Brand Manager</div>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800/50'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-brand-500/20 text-brand-300 font-semibold uppercase tracking-wider">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Section */}
      <div className="p-4 border-t border-surface-800/80 text-[11px] text-slate-500">
        <div className="flex items-center justify-between mb-1">
          <span>Architecture</span>
          <span className="text-emerald-400 font-medium font-mono text-[10px]">Strictly Free</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Build Milestone</span>
          <span className="text-brand-400 font-medium font-mono text-[10px]">Phase 1 Active</span>
        </div>
      </div>
    </aside>
  );
};
