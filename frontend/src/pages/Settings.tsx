import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Bell,
  Cpu,
  Folder,
  Download,
  Trash2,
  CheckCircle,
  Sun,
  Moon,
  Clock,
  Sparkles,
} from 'lucide-react';
import { UserSettings } from '../types';
import { api } from '../services/api';

interface SettingsProps {
  settings: UserSettings | null;
  onSettingsUpdated: (updated: UserSettings) => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Settings: React.FC<SettingsProps> = ({
  settings,
  onSettingsUpdated,
  theme,
  onToggleTheme,
}) => {
  const [remindersEnabled, setRemindersEnabled] = useState(settings?.reminders_enabled ?? true);
  const [intervalMins, setIntervalMins] = useState(settings?.reminder_interval_mins ?? 15);
  const [aiProvider, setAiProvider] = useState(settings?.preferred_ai_provider ?? 'gemini');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [aiProviderStatus, setAIProviderStatus] = useState<{
    gemini_configured: boolean;
    groq_configured: boolean;
  } | null>(null);
  const [aiProviderError, setAIProviderError] = useState('');

  useEffect(() => {
    let active = true;
    void api.getAIProviderStatus().then((response) => {
      if (!active) return;
      if (response.success && response.data) {
        setAIProviderStatus(response.data);
      } else {
        setAIProviderError(response.error?.message ?? 'Could not load AI provider status.');
      }
    });
    return () => {
      active = false;
    };
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveError('');
    const res = await api.updateSettings({
      reminders_enabled: remindersEnabled,
      reminder_interval_mins: intervalMins,
      preferred_ai_provider: aiProvider,
    });
    setSaving(false);
    if (res.success && res.data) {
      onSettingsUpdated(res.data);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } else {
      setSaveError(res.error?.message ?? 'Could not save settings.');
    }
  };

  const handleExportSettings = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(settings, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `brand_agent_backup_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="p-4 rounded-xl bg-surface-900 border border-surface-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-brand-400" />
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Settings & Privacy Centre</h3>
            <p className="text-xs text-slate-400">Manage saved preferences and check configured AI providers.</p>
          </div>
        </div>
      </div>

      {/* 15-Minute Daily Standup Reminders */}
      <div className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-brand-400" />
            <h4 className="text-sm font-bold text-slate-100">Windows Desktop Interview Reminders</h4>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={remindersEnabled}
              onChange={(e) => setRemindersEnabled(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-surface-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-brand-600"></div>
          </label>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Install and run the Windows Desktop Companion for system notifications. It checks these saved preferences and stops reminding after today's interview is complete.
        </p>

        <div className="flex items-center gap-3 pt-2">
          <label className="text-xs text-slate-400">Reminder Interval:</label>
          <select
            value={intervalMins}
            onChange={(e) => setIntervalMins(Number(e.target.value))}
            className="bg-surface-950 border border-surface-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
          >
            <option value={15}>Every 15 minutes (Recommended)</option>
            <option value={30}>Every 30 minutes</option>
            <option value={60}>Every 60 minutes</option>
          </select>
        </div>
      </div>

      {/* AI Engine & Zero Cost Configuration */}
      <div className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-brand-400" />
          <h4 className="text-sm font-bold text-slate-100">Zero-Cost AI Engine Provider</h4>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Gemini and Groq can humanize interview notes into editable drafts using their free tiers (subject to each provider's quotas and terms). Keys stay on the backend; the app never returns them to this page.
        </p>

        {aiProviderError && <p role="alert" className="text-xs text-red-300">{aiProviderError}</p>}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <button
            onClick={() => setAiProvider('gemini')}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              aiProvider === 'gemini'
                ? 'bg-brand-600/15 border-brand-500/40 text-brand-300'
                : 'bg-surface-950 border-surface-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="font-semibold text-xs text-slate-100 mb-1">Google Gemini 2.5</div>
            <div className="text-[11px] text-slate-400">
              {aiProviderStatus?.gemini_configured ? 'API key configured' : 'API key not configured'}
            </div>
            <div className={`text-[10px] mt-2 font-mono ${aiProviderStatus?.gemini_configured ? 'text-emerald-300' : 'text-amber-300'}`}>
              {aiProviderStatus?.gemini_configured ? 'Ready for AI drafts' : 'Set GEMINI_API_KEY on backend'}
            </div>
          </button>

          <button
            onClick={() => setAiProvider('groq')}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              aiProvider === 'groq'
                ? 'bg-brand-600/15 border-brand-500/40 text-brand-300'
                : 'bg-surface-950 border-surface-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="font-semibold text-xs text-slate-100 mb-1">Groq (Llama 3.3)</div>
            <div className="text-[11px] text-slate-400">
              {aiProviderStatus?.groq_configured ? 'API key configured' : 'API key not configured'}
            </div>
            <div className={`text-[10px] mt-2 font-mono ${aiProviderStatus?.groq_configured ? 'text-emerald-300' : 'text-amber-300'}`}>
              {aiProviderStatus?.groq_configured ? 'Ready for AI drafts' : 'Set GROQ_API_KEY on backend'}
            </div>
          </button>

          <button
            onClick={() => setAiProvider('local')}
            disabled
            className={`p-3.5 rounded-xl border text-left transition-all ${
              aiProvider === 'local'
                ? 'bg-brand-600/15 border-brand-500/40 text-brand-300'
                : 'bg-surface-950 border-surface-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <div className="font-semibold text-xs text-slate-100 mb-1">Local SLM (CPU)</div>
            <div className="text-[11px] text-slate-400">Not implemented</div>
            <div className="text-[10px] text-amber-300 mt-2 font-mono">Unavailable</div>
          </button>
        </div>
        <p className="text-xs text-slate-400">
          For local PowerShell, set the key in the backend terminal before starting it; Docker users can place it in the private root <code className="text-slate-200">.env</code>. For a hosted site, add it in the hosting service's environment settings. Never put keys in frontend files or commit them.
        </p>
      </div>

      {/* Privacy Centre & Data Sovereignty */}
      <div className="p-6 rounded-xl bg-surface-900 border border-surface-800 space-y-4">
        <h4 className="text-sm font-bold text-slate-100">Privacy Centre & Data Ownership</h4>
        <p className="text-xs text-slate-300 leading-relaxed">
          Records are stored in the database configured for this deployment. Cross-device cloud synchronization and complete privacy controls are not implemented yet.
        </p>

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            onClick={handleExportSettings}
            className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium bg-surface-800 hover:bg-surface-700 text-slate-200 border border-slate-700/50 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Settings (.json)</span>
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end gap-3 pt-4">
        {saveError && <span role="alert" className="text-xs text-red-300">{saveError}</span>}
        {saveSuccess && (
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
            <CheckCircle className="w-4 h-4" />
            <span>Settings saved successfully</span>
          </span>
        )}
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2.5 rounded-xl text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white transition-all shadow-md shadow-brand-500/20 disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};
