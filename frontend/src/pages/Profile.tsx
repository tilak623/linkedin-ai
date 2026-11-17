import React, { FormEvent, useEffect, useState } from 'react';
import { Plus, Save, Trash2, UserRound } from 'lucide-react';
import { api } from '../services/api';
import { OnboardingInput, SkillTier } from '../types';

interface InitialSkill {
  name: string;
  proficiency_level: SkillTier;
  category: string;
  evidence_notes: string;
}

const EMPTY_SKILL: InitialSkill = {
  name: '',
  proficiency_level: 'discovered',
  category: '',
  evidence_notes: '',
};

const inputClass = 'w-full rounded-lg border border-surface-700 bg-surface-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-brand-500 focus:outline-none';
const labelClass = 'mb-1 block text-xs font-medium text-slate-300';

interface ProfileProps {
  onOnboardingComplete: (fullName: string) => void;
}

export const Profile: React.FC<ProfileProps> = ({ onOnboardingComplete }) => {
  const [fullName, setFullName] = useState('');
  const [headline, setHeadline] = useState('');
  const [summary, setSummary] = useState('');
  const [careerDirection, setCareerDirection] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [writingVoice, setWritingVoice] = useState('');
  const [seniority, setSeniority] = useState('');
  const [initialSkills, setInitialSkills] = useState<InitialSkill[]>([{ ...EMPTY_SKILL }]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;
    const loadProfile = async () => {
      const [profileResult, authResult] = await Promise.all([
        api.getProfile(),
        api.getAuthStatus(),
      ]);
      if (!active) return;
      if (profileResult.success && profileResult.data) {
        const profile = profileResult.data;
        setHeadline(profile.headline ?? '');
        setSummary(profile.summary ?? '');
        setCareerDirection(profile.career_direction ?? '');
        setTargetAudience(profile.target_audience ?? '');
        setWritingVoice(profile.writing_voice_notes ?? '');
        setSeniority(profile.seniority_level ?? '');
      } else {
        setError(profileResult.error?.message ?? 'Could not load your profile.');
      }
      if (authResult.success && authResult.data) {
        setFullName(authResult.data.full_name ?? '');
      } else if (!profileResult.error) {
        setError(authResult.error?.message ?? 'Could not load your account details.');
      }
      setLoading(false);
    };
    void loadProfile();
    return () => { active = false; };
  }, []);

  const updateSkill = (index: number, patch: Partial<InitialSkill>) => {
    setInitialSkills((skills) => skills.map((skill, i) => i === index ? { ...skill, ...patch } : skill));
  };

  const submitOnboarding = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    setSaved(false);
    const payload: OnboardingInput = {
      full_name: fullName.trim(),
      headline: headline.trim() || null,
      summary: summary.trim() || null,
      career_direction: careerDirection.trim() || null,
      target_audience: targetAudience.trim() || null,
      writing_voice_notes: writingVoice.trim() || null,
      seniority_level: seniority.trim() || null,
      initial_skills: initialSkills
        .filter((skill) => skill.name.trim())
        .map((skill) => ({
          name: skill.name.trim(),
          proficiency_level: skill.proficiency_level,
          category: skill.category.trim() || null,
          evidence_notes: skill.evidence_notes.trim() || null,
          verified_by_project: false,
        })),
    };
    const result = await api.completeOnboarding(payload);
    setSaving(false);
    if (!result.success || !result.data) {
      setError(result.error?.message ?? 'Could not save your onboarding details.');
      return;
    }
    onOnboardingComplete(payload.full_name);
    setSaved(true);
    setInitialSkills([{ ...EMPTY_SKILL }]);
  };

  if (loading) {
    return <p className="text-sm text-slate-400">Loading professional profile…</p>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header className="flex items-start gap-3 rounded-xl border border-surface-800 bg-surface-900 p-5">
        <UserRound className="mt-0.5 h-5 w-5 text-brand-400" />
        <div>
          <h2 className="text-base font-semibold text-slate-100">Professional onboarding</h2>
          <p className="mt-1 text-xs leading-relaxed text-slate-400">
            Add your real background and preferences. These details are saved to the local profile and can be updated later.
          </p>
        </div>
      </header>

      <form onSubmit={submitOnboarding} className="space-y-5 rounded-xl border border-surface-800 bg-surface-900 p-6">
        <section className="grid gap-4 sm:grid-cols-2">
          <label>
            <span className={labelClass}>Full name *</span>
            <input required maxLength={200} className={inputClass} value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </label>
          <label>
            <span className={labelClass}>Professional headline</span>
            <input maxLength={300} className={inputClass} value={headline} onChange={(e) => setHeadline(e.target.value)} />
          </label>
          <label>
            <span className={labelClass}>Career direction</span>
            <input maxLength={2000} className={inputClass} value={careerDirection} onChange={(e) => setCareerDirection(e.target.value)} />
          </label>
          <label>
            <span className={labelClass}>Target audience</span>
            <input maxLength={2000} className={inputClass} value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} />
          </label>
          <label>
            <span className={labelClass}>Career level (optional)</span>
            <input maxLength={100} className={inputClass} value={seniority} onChange={(e) => setSeniority(e.target.value)} />
          </label>
          <label className="sm:col-span-2">
            <span className={labelClass}>About your professional background</span>
            <textarea rows={4} maxLength={8000} className={inputClass} value={summary} onChange={(e) => setSummary(e.target.value)} />
          </label>
          <label className="sm:col-span-2">
            <span className={labelClass}>Writing preferences</span>
            <textarea rows={3} maxLength={4000} className={inputClass} value={writingVoice} onChange={(e) => setWritingVoice(e.target.value)} placeholder="Tone, wording, or styles you prefer or want to avoid" />
          </label>
        </section>

        <section className="space-y-3 border-t border-surface-800 pt-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Current skills</h3>
              <p className="mt-1 text-xs text-slate-400">Choose the level that accurately describes your experience.</p>
            </div>
            <button type="button" onClick={() => setInitialSkills((items) => [...items, { ...EMPTY_SKILL }])} className="inline-flex items-center gap-1 rounded-lg border border-surface-700 px-3 py-2 text-xs text-slate-200 hover:bg-surface-800">
              <Plus className="h-3.5 w-3.5" /> Add skill
            </button>
          </div>
          {initialSkills.map((skill, index) => (
            <div key={index} className="grid gap-2 rounded-lg border border-surface-800 bg-surface-950 p-3 sm:grid-cols-[1fr_150px_1fr_1fr_auto]">
              <input aria-label="Skill name" maxLength={100} className={inputClass} placeholder="Skill name" value={skill.name} onChange={(e) => updateSkill(index, { name: e.target.value })} />
              <select aria-label="Skill experience level" className={inputClass} value={skill.proficiency_level} onChange={(e) => updateSkill(index, { proficiency_level: e.target.value as SkillTier })}>
                <option value="implemented">Implemented</option>
                <option value="studied">Studied</option>
                <option value="explored">Explored</option>
                <option value="discovered">Discovered</option>
              </select>
              <input aria-label="Skill category" maxLength={100} className={inputClass} placeholder="Category (optional)" value={skill.category} onChange={(e) => updateSkill(index, { category: e.target.value })} />
              <input aria-label="Skill evidence" maxLength={4000} className={inputClass} placeholder="Evidence or context (optional)" value={skill.evidence_notes} onChange={(e) => updateSkill(index, { evidence_notes: e.target.value })} />
              <button type="button" aria-label="Remove skill" disabled={initialSkills.length === 1} onClick={() => setInitialSkills((items) => items.filter((_, i) => i !== index))} className="rounded-lg p-2 text-slate-400 hover:bg-rose-950/40 hover:text-rose-300 disabled:opacity-40">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </section>

        {error && <p role="alert" className="rounded-lg border border-rose-800/50 bg-rose-950/30 p-3 text-sm text-rose-300">{error}</p>}
        {saved && <p role="status" className="rounded-lg border border-emerald-800/50 bg-emerald-950/30 p-3 text-sm text-emerald-300">Profile saved.</p>}

        <div className="flex justify-end border-t border-surface-800 pt-4">
          <button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-500 disabled:opacity-50">
            <Save className="h-4 w-4" />
            {saving ? 'Saving…' : 'Save onboarding'}
          </button>
        </div>
      </form>
    </div>
  );
};
