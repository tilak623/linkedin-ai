import React, { useState } from 'react';
import { Image, Code, FileText, Download, Sparkles, Layout } from 'lucide-react';

export const MediaStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'infographic' | 'code' | 'carousel'>('code');

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Studio Header Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-800 pb-3">
        <button
          onClick={() => setActiveTab('code')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'code'
              ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'
          }`}
        >
          <Code className="w-4 h-4" />
          <span>Code Snippet Card</span>
        </button>

        <button
          onClick={() => setActiveTab('infographic')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'infographic'
              ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'
          }`}
        >
          <Image className="w-4 h-4" />
          <span>Technical Architecture Card</span>
        </button>

        <button
          onClick={() => setActiveTab('carousel')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'carousel'
              ? 'bg-brand-600/15 text-brand-400 border border-brand-500/30 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-surface-800'
          }`}
        >
          <Layout className="w-4 h-4" />
          <span>Multi-Slide Carousel (PDF)</span>
        </button>
      </div>

      {/* Media Canvas Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Settings / Parameters */}
        <div className="space-y-4">
          <div className="rounded-xl bg-surface-900 border border-surface-800 p-5 space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Card Properties</h3>
            
            <div>
              <label className="text-xs text-slate-300 block mb-1">Snippet Title</label>
              <input
                type="text"
                defaultValue="Zero-Lock SQLite Connection Manager"
                className="w-full bg-surface-950 border border-surface-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500"
              />
            </div>

            <div>
              <label className="text-xs text-slate-300 block mb-1">Theme Palette</label>
              <select className="w-full bg-surface-950 border border-surface-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-brand-500">
                <option>Obsidian Dark (LinkedIn Optimized)</option>
                <option>Deep Navy Blue</option>
                <option>Minimal Clean Light</option>
              </select>
            </div>

            <div className="pt-2">
              <button className="w-full py-2.5 px-3 rounded-lg text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white flex items-center justify-center gap-2 transition-all shadow-sm shadow-brand-500/20">
                <Download className="w-3.5 h-3.5" />
                <span>Export High-Res PNG (1200x675)</span>
              </button>
            </div>
          </div>
        </div>

        {/* Live Canvas Preview */}
        <div className="lg:col-span-2">
          <div className="rounded-xl bg-surface-900 border border-surface-800 p-6 flex flex-col items-center justify-center min-h-[380px]">
            {/* Visual Card Mock */}
            <div className="w-full max-w-lg rounded-2xl bg-surface-950 border border-surface-700/60 p-6 shadow-2xl relative overflow-hidden">
              <div className="flex items-center justify-between pb-4 border-b border-surface-800">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                  <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                  <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">connection_manager.py</span>
              </div>

              <div className="py-4 font-mono text-xs text-slate-300 leading-relaxed space-y-1">
                <div><span className="text-indigo-400">@contextmanager</span></div>
                <div><span className="text-rose-400">def</span> <span className="text-brand-400">get_connection</span>(db_path):</div>
                <div className="pl-4">conn = sqlite3.<span className="text-amber-400">connect</span>(db_path, timeout=<span className="text-emerald-400">10.0</span>)</div>
                <div className="pl-4">conn.execute(<span className="text-emerald-300">"PRAGMA foreign_keys = ON;"</span>)</div>
                <div className="pl-4"><span className="text-rose-400">try</span>:</div>
                <div className="pl-8"><span className="text-rose-400">yield</span> conn</div>
                <div className="pl-4"><span className="text-rose-400">finally</span>:</div>
                <div className="pl-8">conn.<span className="text-amber-400">close</span>()</div>
              </div>

              <div className="pt-4 border-t border-surface-800 flex items-center justify-between text-[10px] text-slate-500">
                <span>Personal Branding AI Agent</span>
                <span className="text-brand-400 font-medium">Free Programmatic Engine</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
