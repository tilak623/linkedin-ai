import React from 'react';
import { Compass, ExternalLink, ShieldCheck, Flame, Bookmark } from 'lucide-react';

export const Research: React.FC = () => {
  const discoveries = [
    {
      source: 'Hacker News',
      credibility: 0.92,
      category: 'AI & Systems',
      title: 'Small Language Models Running on Edge Devices: Lessons from Production',
      summary: 'Practical evaluation of running quantized 1.5B–3B parameter models on consumer hardware without dedicated GPUs.',
      link: 'https://news.ycombinator.com',
      classification: 'Educational Post Potential',
    },
    {
      source: 'ArXiv',
      credibility: 0.98,
      category: 'Machine Learning',
      title: 'Efficient Speculative Decoding Techniques for Real-Time LLM Inference',
      summary: 'Novel algorithmic approach to reduce latency by 40% with zero loss in output quality.',
      link: 'https://arxiv.org',
      classification: 'Research Note Saved',
    },
    {
      source: 'GitHub Trending',
      credibility: 0.88,
      category: 'Developer Tooling',
      title: 'Lightweight Local Agent Architectures with Hybrid Synchronous Storage',
      summary: 'Open-source benchmark comparing persistent embedded stores for AI companions.',
      link: 'https://github.com/trending',
      classification: 'Interview Discussion Topic',
    },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between p-4 rounded-xl bg-surface-900 border border-surface-800">
        <div className="flex items-center gap-3">
          <Compass className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Daily Technology Research</h3>
            <p className="text-xs text-slate-400">Multi-source automated tech discoveries filtered by credibility score.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {discoveries.map((item, idx) => (
          <div key={idx} className="p-5 rounded-xl bg-surface-900 border border-surface-800 hover:border-surface-700/80 transition-colors space-y-3">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-brand-400">{item.source}</span>
                <span className="text-slate-500">•</span>
                <span className="text-slate-400">{item.category}</span>
                <span className="text-slate-500">•</span>
                <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>{Math.round(item.credibility * 100)}% Credibility</span>
                </span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] bg-brand-500/10 text-brand-300 font-mono">
                {item.classification}
              </span>
            </div>

            <h4 className="text-base font-bold text-slate-100">{item.title}</h4>
            <p className="text-xs text-slate-300 leading-relaxed">{item.summary}</p>

            <div className="pt-1 flex items-center justify-between text-xs">
              <a
                href={item.link}
                target="_blank"
                rel="noreferrer"
                className="text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium transition-colors"
              >
                <span>Read Verified Source</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
              <button className="flex items-center gap-1 text-slate-400 hover:text-slate-200 transition-colors">
                <Bookmark className="w-3.5 h-3.5" />
                <span>Save to Notes</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
