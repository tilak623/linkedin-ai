import React from 'react';
import { FolderGit2, Star, GitFork, ExternalLink, CheckCircle } from 'lucide-react';

export const Portfolio: React.FC = () => {
  const projects = [
    {
      title: 'Personal Branding AI Agent',
      maturity: 'in_development',
      description: 'Intelligent desktop assistant that interviews engineers, tracks skills, and creates authentic LinkedIn posts with zero-cost AI models.',
      techStack: ['Python', 'FastAPI', 'React', 'TypeScript', 'Electron', 'SQLite'],
      achievements: [
        'Built zero-lock connection manager for Windows SQLite storage',
        'Engineered 12-module executive branding command center',
        'Implemented Web Speech API for free in-browser daily standups',
      ],
      githubUrl: 'https://github.com/developer/personal-branding-agent',
    },
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FolderGit2 className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Portfolio & Project Intelligence</h3>
            <p className="text-xs text-slate-400">Accurate project tracking with maturity classification. Never exaggerates contributions.</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {projects.map((proj, idx) => (
          <div key={idx} className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-base font-bold text-slate-100">{proj.title}</h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-brand-500/10 text-brand-300 capitalize border border-brand-500/20">
                    {proj.maturity.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">{proj.description}</p>
              </div>
              <a
                href={proj.githubUrl}
                target="_blank"
                rel="noreferrer"
                className="p-2 rounded-lg bg-surface-800 hover:bg-surface-700 text-slate-300 hover:text-white transition-colors"
                title="View on GitHub"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* Tech Stack Pills */}
            <div className="flex flex-wrap gap-1.5">
              {proj.techStack.map((tech) => (
                <span key={tech} className="px-2 py-0.5 rounded text-[11px] font-mono bg-surface-950 text-slate-300 border border-surface-800">
                  {tech}
                </span>
              ))}
            </div>

            {/* Achievements / Evidence */}
            <div className="pt-2 border-t border-surface-800/80 space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Verified Engineering Milestones
              </span>
              {proj.achievements.map((ach, i) => (
                <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{ach}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
