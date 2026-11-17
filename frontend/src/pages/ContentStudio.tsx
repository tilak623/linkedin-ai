import React, { useState } from 'react';
import { PenTool, CheckCircle, ShieldCheck, Copy, ExternalLink, Sparkles, AlertTriangle } from 'lucide-react';

export const ContentStudio: React.FC = () => {
  const [selectedDraft, setSelectedDraft] = useState<number>(0);
  const [copied, setCopied] = useState(false);

  const drafts = [
    {
      id: 1,
      title: 'Architecting an Asynchronous Database Layer with Zero External Dependencies',
      format: 'Technical Deep-Dive',
      tone: 'Engineering Direct',
      hook: "Most developers assume you need heavy third-party ORMs for fast SQLite in Python. Here's what we learned building without them:",
      content: `When designing the backend for an intelligent desktop agent, resource conservation isn't a bonus—it's a requirement.\n\nHere were the constraints:\n1. 100% offline-first capability\n2. Sub-millisecond queries on local SSD\n3. Zero risk of database lock freezes on Windows\n\nInstead of pulling in a massive async ORM with dozens of dependencies, we paired standard library \`sqlite3\` with threadpool delegators and strict transaction boundaries.\n\nKey takeaways:\n• PRAGMA journal_mode matters: on synchronized cloud folders, standard rollback modes prevent concurrency lock stalls.\n• Pure Python dataclasses or Pydantic schemas serialize faster than heavy relational abstractions.\n• Simple architecture is easier to audit and impossible to break with upstream dependency rot.\n\nWhat's your preferred approach for local embedded storage in Python?`,
      hashtags: ['#Python', '#SoftwareEngineering', '#SystemDesign', '#BackendDevelopment'],
      status: 'pending_approval',
    },
  ];

  const handleCopy = () => {
    const post = drafts[selectedDraft];
    const fullText = `${post.hook}\n\n${post.content}\n\n${post.hashtags.join(' ')}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenLinkedIn = () => {
    window.open('https://www.linkedin.com/feed/', '_blank');
  };

  const activeDraft = drafts[selectedDraft];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Principle Callout */}
      <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 flex items-start gap-3 text-xs text-amber-300">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-amber-200">Strict Human Approval Enforced: </span>
          The AI never publishes autonomously. Every post requires your review, fact-check validation, and manual confirmation.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Drafts List */}
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Available Drafts</h3>
          {drafts.map((draft, idx) => (
            <button
              key={draft.id}
              onClick={() => setSelectedDraft(idx)}
              className={`w-full text-left p-4 rounded-xl border transition-all ${
                selectedDraft === idx
                  ? 'bg-surface-800 border-brand-500/40 text-slate-100 shadow-md'
                  : 'bg-surface-900 border-surface-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center justify-between text-[11px] mb-1.5">
                <span className="text-brand-400 font-medium">{draft.format}</span>
                <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono text-[10px]">
                  Pending Review
                </span>
              </div>
              <div className="text-sm font-semibold line-clamp-2 text-slate-200 mb-2">{draft.title}</div>
              <div className="text-xs text-slate-400 line-clamp-2">{draft.hook}</div>
            </button>
          ))}
        </div>

        {/* Post Editor & Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl bg-surface-900 border border-surface-800 p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-surface-800 pb-3">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">LinkedIn Post Preview</span>
                <h4 className="text-sm font-bold text-slate-100 mt-0.5">{activeDraft.title}</h4>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Anti-Cliché Verified</span>
                </span>
              </div>
            </div>

            {/* Post Content Body */}
            <div className="p-4 rounded-lg bg-surface-950 border border-surface-800/80 font-sans text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
              <p className="font-medium text-slate-100 mb-3">{activeDraft.hook}</p>
              <p>{activeDraft.content}</p>
              <div className="mt-4 pt-3 border-t border-surface-800/60 flex flex-wrap gap-1.5 text-xs text-brand-400 font-mono">
                {activeDraft.hashtags.map((h) => (
                  <span key={h}>{h}</span>
                ))}
              </div>
            </div>

            {/* Action Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <div className="text-xs text-slate-400 flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span>Fact-checked against daily interview</span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-700 text-slate-200 border border-slate-700/50 transition-colors"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{copied ? 'Copied to Clipboard!' : 'Copy Post'}</span>
                </button>

                <button
                  onClick={handleOpenLinkedIn}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white transition-all shadow-sm shadow-brand-500/20"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open LinkedIn to Publish</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
