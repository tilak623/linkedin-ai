import React from 'react';
import { Users, UserPlus, MessageSquare, ShieldCheck, AlertTriangle } from 'lucide-react';

export const Networking: React.FC = () => {
  const opportunities = [
    {
      name: 'Sarah Chen',
      role: 'Staff Infrastructure Engineer at AI Startup',
      context: 'Sarah published a technical thread analyzing SQLite concurrency trade-offs on Windows and cloud sync drives.',
      proposedAction: 'Thoughtful discussion comment',
      draftMessage: 'Excellent analysis on file-lock semantics! We hit the exact same lock stall with SQLite WAL mode in synchronized cloud folders and resolved it by switching to atomic rollback journaling with strict connection pooling.',
      status: 'pending_approval',
    },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Principle Callout */}
      <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 flex items-start gap-3 text-xs text-amber-300">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-200">Zero Autonomous Outreach: </span>
          The AI drafts thoughtful, personalized contributions based on technical synergy, but will never send messages or comments without your explicit manual review.
        </div>
      </div>

      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Professional Networking Assistant</h3>
            <p className="text-xs text-slate-400">Identifies genuine technical synergies. Avoids generic spam connection requests.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {opportunities.map((opp, idx) => (
          <div key={idx} className="p-5 rounded-xl bg-surface-900 border border-surface-800 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-100">{opp.name}</h4>
                <div className="text-xs text-brand-400">{opp.role}</div>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Approval Required
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-surface-950 p-3 rounded-lg border border-surface-800/80">
              <span className="font-semibold text-slate-400">Context: </span>
              {opp.context}
            </p>

            <div className="p-3.5 rounded-lg bg-surface-950 border border-surface-800 space-y-1.5">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">
                Drafted Contribution ({opp.proposedAction})
              </span>
              <p className="text-xs text-slate-200 italic leading-relaxed">"{opp.draftMessage}"</p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-1">
              <button className="px-3 py-1.5 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-700 text-slate-300 transition-colors">
                Edit Draft
              </button>
              <button className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white transition-all shadow-sm shadow-brand-500/20">
                Copy & Open Discussion
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
