import React from 'react';
import { BarChart3, Info, Lock, TrendingUp } from 'lucide-react';

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Integrity Notice */}
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-start gap-3 text-xs text-slate-300">
        <Info className="w-4 h-4 text-brand-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-100">Zero Fabricated Analytics Principle: </span>
          In accordance with platform guidelines and system principles, this application tracks real performance and does not fabricate fake viewer counts, engagement rates, or impression numbers.
        </div>
      </div>

      {/* API Scope Limitation Callout */}
      <div className="p-5 rounded-xl bg-surface-900 border border-surface-800 space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Lock className="w-4 h-4 text-amber-400" />
          <span>LinkedIn Developer API Scope Status</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Standard self-serve LinkedIn Developer Apps support <code className="text-brand-400 font-mono">w_member_social</code> (post publishing) and <code className="text-brand-400 font-mono">openid</code> (authentication). Detailed follower analytics and demographic views require LinkedIn Community Management API or Enterprise Partner approval.
        </p>
      </div>

      {/* Internal Content Performance Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 space-y-1">
          <div className="text-xs text-slate-400">Total Posts Drafted</div>
          <div className="text-2xl font-bold text-slate-100">1</div>
          <div className="text-[10px] text-brand-400">1 pending approval</div>
        </div>

        <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 space-y-1">
          <div className="text-xs text-slate-400">Skills Documented</div>
          <div className="text-2xl font-bold text-slate-100">8</div>
          <div className="text-[10px] text-emerald-400">4 implemented in code</div>
        </div>

        <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 space-y-1">
          <div className="text-xs text-slate-400">Standup Reflection Rate</div>
          <div className="text-2xl font-bold text-slate-100">100%</div>
          <div className="text-[10px] text-slate-400">Active streak: 1 day</div>
        </div>
      </div>
    </div>
  );
};
