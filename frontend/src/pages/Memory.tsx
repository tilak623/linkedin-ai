import React, { useState } from 'react';
import { Brain, CheckCircle, Search, BookOpen, Compass, Sparkles } from 'lucide-react';

export const Memory: React.FC = () => {
  const [activeTier, setActiveTier] = useState<string>('all');

  const skills = [
    { name: 'Python 3.13', tier: 'implemented', evidence: 'Built asynchronous local backend with zero external dependencies', category: 'Backend & Systems' },
    { name: 'FastAPI & Pydantic v2', tier: 'implemented', evidence: 'Designed REST endpoints with strict typing and schema validation', category: 'Web Framework' },
    { name: 'SQLite Architecture', tier: 'implemented', evidence: 'Implemented zero-lock synchronous connection manager for Windows', category: 'Databases' },
    { name: 'React & TypeScript', tier: 'implemented', evidence: 'Engineered multi-workspace executive branding interface', category: 'Frontend' },
    { name: 'Electron IPC Architecture', tier: 'studied', evidence: 'Analyzed native tray management and 15-minute background timer lifecycles', category: 'Desktop' },
    { name: 'Quantized SLM ONNX Runtimes', tier: 'studied', evidence: 'Evaluated SmolLM2-1.7B and Qwen2.5-1.5B CPU AVX2 performance profiles', category: 'AI/ML' },
    { name: 'Supabase Row Level Security', tier: 'explored', evidence: 'Tested PostgreSQL multi-tenant isolation policies', category: 'Cloud Security' },
    { name: 'Whisper-tiny Local Audio Engine', tier: 'discovered', evidence: 'Saved for future offline voice transcription evaluation', category: 'Voice AI' },
  ];

  const filtered = activeTier === 'all' ? skills : skills.filter((s) => s.tier === activeTier);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Knowledge Library Header */}
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Professional Memory & Knowledge Library</h3>
            <p className="text-xs text-slate-400">Strictly distinguishes between implemented, studied, explored, and discovered skills.</p>
          </div>
        </div>
      </div>

      {/* Tier Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2">
        {['all', 'implemented', 'studied', 'explored', 'discovered'].map((tier) => (
          <button
            key={tier}
            onClick={() => setActiveTier(tier)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
              activeTier === tier
                ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 font-semibold'
                : 'text-slate-400 hover:text-slate-200 bg-surface-900 border border-surface-800'
            }`}
          >
            {tier} {tier !== 'all' && `(${skills.filter((s) => s.tier === tier).length})`}
          </button>
        ))}
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((skill, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-surface-900 border border-surface-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-slate-100">{skill.name}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium capitalize ${
                  skill.tier === 'implemented'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : skill.tier === 'studied'
                    ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
                    : skill.tier === 'explored'
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    : 'bg-slate-700/30 text-slate-400 border border-slate-700'
                }`}
              >
                {skill.tier}
              </span>
            </div>
            <div className="text-[11px] text-brand-400 font-medium">{skill.category}</div>
            <div className="text-xs text-slate-400 leading-relaxed pt-1 border-t border-surface-800/60">
              <span className="text-slate-500">Evidence: </span>
              {skill.evidence}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
