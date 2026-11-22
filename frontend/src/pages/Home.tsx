import React from 'react';
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Brain,
  Shield,
  Layers,
  Cpu,
} from 'lucide-react';
import { HealthResponse, UserAuthStatus, WorkspaceView } from '../types';

interface HomeProps {
  onNavigate: (view: WorkspaceView) => void;
  health: HealthResponse | null;
  authStatus: UserAuthStatus | null;
}

export const Home: React.FC<HomeProps> = ({ onNavigate, health, authStatus }) => {
  return (
    <div className="space-y-6">
      {/* Top Banner: Daily Interview Callout */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-900/60 via-indigo-950/40 to-surface-900 border border-brand-500/20 p-6 md:p-8">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-brand-500/20 text-brand-300 border border-brand-500/30 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Today's Daily Standup Available</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">
            What technical milestone or problem did you solve today?
          </h2>
          <p className="text-sm text-slate-300 mb-6 leading-relaxed">
            Your branding assistant is ready to interview you. A quick 3-minute voice or text reflection will capture
            your genuine learning breakthroughs and translate them into authentic LinkedIn insights.
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate('interview')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-brand-500 hover:bg-brand-400 text-white transition-all shadow-lg shadow-brand-500/25"
            >
              <Sparkles className="w-4 h-4" />
              <span>Start Daily Interview</span>
            </button>
            <button
              onClick={() => onNavigate('research')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium bg-surface-800 hover:bg-surface-800/80 text-slate-200 border border-slate-700/50 transition-colors"
            >
              <span>Explore Today's Tech Research</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="absolute right-0 bottom-0 opacity-10 pointer-events-none transform translate-x-12 translate-y-12">
          <Brain className="w-96 h-96 text-brand-400" />
        </div>
      </div>

      {/* Grid of Key Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Card 1: Content Studio & Approval Checkpoint */}
        <div className="rounded-xl bg-surface-900 border border-surface-800 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Content Studio</span>
              <span className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <AlertTriangle className="w-4 h-4" />
              </span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">In development</div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Post generation, fact checking, and publishing are planned for a later phase.
            </p>
          </div>
          <button
            onClick={() => onNavigate('content')}
            className="mt-4 w-full py-2 px-3 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-800/80 text-slate-200 border border-slate-700/50 flex items-center justify-center gap-1.5 transition-colors"
          >
            <span>Open Content Studio</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 2: Professional Memory & Skills */}
        <div className="rounded-xl bg-surface-900 border border-surface-800 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Knowledge Hierarchy</span>
              <span className="p-1.5 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
                <Brain className="w-4 h-4" />
              </span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">4 Skill Levels</div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Record skills as Implemented, Studied, Explored, or Discovered in your professional memory.
            </p>
          </div>
          <button
            onClick={() => onNavigate('memory')}
            className="mt-4 w-full py-2 px-3 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-800/80 text-slate-200 border border-slate-700/50 flex items-center justify-center gap-1.5 transition-colors"
          >
            <span>Review Memory Library</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Card 3: Free Zero-Cost Engine Status */}
        <div className="rounded-xl bg-surface-900 border border-surface-800 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Engine Profile</span>
              <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Shield className="w-4 h-4" />
              </span>
            </div>
            <div className="text-2xl font-bold text-white mb-1">
              {health?.ai_provider === 'local_fallback'
                ? 'AI key not configured'
                : `${health?.ai_provider ?? 'Checking'} provider`}
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Interview notes can be turned into editable AI drafts when a provider key is configured. Cloud sync is not enabled.
            </p>
          </div>
          <button
            onClick={() => onNavigate('settings')}
            className="mt-4 w-full py-2 px-3 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-800/80 text-slate-200 border border-slate-700/50 flex items-center justify-center gap-1.5 transition-colors"
          >
            <span>View System Settings</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* System Resources & Architecture Diagnostics */}
      <div className="rounded-xl bg-surface-900 border border-surface-800 p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-brand-400" />
          <span>Host Hardware & Resource Telemetry</span>
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3.5 rounded-lg bg-surface-950 border border-surface-800/80">
            <div className="text-[11px] text-slate-400">Compute Threads</div>
            <div className="text-lg font-bold text-slate-100 mt-1">
              {health?.resources.cpu_cores ?? '—'} Logical Cores
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Reported by local backend</div>
          </div>
          <div className="p-3.5 rounded-lg bg-surface-950 border border-surface-800/80">
            <div className="text-[11px] text-slate-400">Physical Memory</div>
            <div className="text-lg font-bold text-slate-100 mt-1">
              {health?.resources.total_ram_gb ?? '—'} GB Total
            </div>
            <div className="text-[10px] text-emerald-400 mt-0.5">
              {health?.resources.available_ram_gb ?? '—'} GB Available
            </div>
          </div>
          <div className="p-3.5 rounded-lg bg-surface-950 border border-surface-800/80">
            <div className="text-[11px] text-slate-400">Storage Capacity</div>
            <div className="text-lg font-bold text-slate-100 mt-1">
              {health?.resources.free_disk_gb ?? '—'} GB Free
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5">Reported by local backend</div>
          </div>
          <div className="p-3.5 rounded-lg bg-surface-950 border border-surface-800/80">
            <div className="text-[11px] text-slate-400">Database Engine</div>
            <div className="text-lg font-bold text-slate-100 mt-1 capitalize">
              {health?.database || 'Status unavailable'}
            </div>
            <div className="text-[10px] text-brand-400 mt-0.5">Local database</div>
          </div>
        </div>
      </div>
    </div>
  );
};
