import React from 'react';
import { UserCheck, Sparkles, Edit3, ArrowRight } from 'lucide-react';

export const Profile: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <UserCheck className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Profile Optimization Manager</h3>
            <p className="text-xs text-slate-400">Positioning analysis and recommendations. Never modifies public profiles without approval.</p>
          </div>
        </div>
      </div>

      {/* Headline Optimizer */}
      <div className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-bold text-slate-100">Current Professional Headline</h4>
          <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Optimized</span>
          </span>
        </div>

        <div className="p-4 rounded-lg bg-surface-950 border border-surface-800 text-sm text-slate-200">
          AI Systems & Full-Stack Engineer | Architecting Intelligent Personal Branding & Zero-Cost Developer Tooling
        </div>

        <div className="p-3.5 rounded-lg bg-brand-950/20 border border-brand-500/20 text-xs text-brand-300 space-y-1">
          <span className="font-semibold text-brand-200">Why this works: </span>
          Balances concrete engineering keywords (AI Systems, Full-Stack) with distinct, memorable problem ownership (Zero-Cost Tooling, Personal Branding).
        </div>
      </div>

      {/* Summary / About Section */}
      <div className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
        <h4 className="text-sm font-bold text-slate-100">About Section Narrative</h4>
        <div className="p-4 rounded-lg bg-surface-950 border border-surface-800 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">
          I build high-reliability software systems and intelligent AI tooling. My work focuses on real-world engineering constraints: offline resilience, sub-millisecond data architectures, and zero operational overhead.
          {'\n\n'}
          Currently architecting full-stack AI assistants that turn daily engineering milestones into authentic professional knowledge.
        </div>
      </div>
    </div>
  );
};
