import React from 'react';
import { Wifi, WifiOff, Cpu, Database } from 'lucide-react';
import { HealthResponse } from '../types';

interface StatusBadgeProps {
  health: HealthResponse | null;
  loading: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ health, loading }) => {
  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-surface-800 text-slate-400 border border-slate-700/50">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
        <span>Connecting to local engine...</span>
      </div>
    );
  }

  const isConnected = health && health.status === 'healthy';

  return (
    <div className="flex items-center gap-3">
      {/* Backend & DB Status */}
      <div
        className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs border ${
          isConnected
            ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40'
            : 'bg-rose-950/40 text-rose-400 border-rose-800/40'
        }`}
      >
        {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
        <span>{isConnected ? 'Engine Online' : 'Offline / Standalone'}</span>
      </div>

      {/* Hardware / RAM Monitor */}
      {health?.resources && (
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-surface-800 text-slate-300 border border-slate-700/50">
          <Cpu className="w-3.5 h-3.5 text-brand-400" />
          <span>
            {health.resources.available_ram_gb} GB RAM Free
          </span>
        </div>
      )}

      {/* AI Provider */}
      {health && (
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-surface-800 text-slate-300 border border-slate-700/50">
          <Database className="w-3.5 h-3.5 text-indigo-400" />
          <span className="capitalize">{health.ai_provider} Engine</span>
        </div>
      )}
    </div>
  );
};
