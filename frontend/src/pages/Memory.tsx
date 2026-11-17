import React, { FormEvent, useCallback, useEffect, useState } from 'react';
import { BookOpen, Download, Pencil, Plus, Search, Trash2 } from 'lucide-react';
import { api } from '../services/api';
import {
  KnowledgeSearchResult,
  LearningMilestone,
  Project,
  ProjectMaturity,
  Skill,
  SkillTier,
} from '../types';

type MemoryTab = 'skills' | 'projects' | 'milestones';

const inputClass = 'w-full rounded-lg border border-surface-700 bg-surface-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-brand-500 focus:outline-none';
const buttonClass = 'inline-flex items-center gap-1.5 rounded-lg border border-surface-700 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-surface-800';

const splitLines = (value: string) => value.split(/\r?\n/).map((part) => part.trim()).filter(Boolean);

export const Memory: React.FC = () => {
  const [activeTab, setActiveTab] = useState<MemoryTab>('skills');
  const [skills, setSkills] = useState<Skill[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [milestones, setMilestones] = useState<LearningMilestone[]>([]);
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResult[] | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(true);

  const [skillName, setSkillName] = useState('');
  const [skillTier, setSkillTier] = useState<SkillTier>('discovered');
  const [skillCategory, setSkillCategory] = useState('');
  const [skillEvidence, setSkillEvidence] = useState('');
  const [skillVerified, setSkillVerified] = useState(false);
  const [editingSkill, setEditingSkill] = useState<Skill | null>(null);

  const [projectTitle, setProjectTitle] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [projectMaturity, setProjectMaturity] = useState<ProjectMaturity>('planned');
  const [projectGithubUrl, setProjectGithubUrl] = useState('');
  const [projectRepoName, setProjectRepoName] = useState('');
  const [projectTech, setProjectTech] = useState('');
  const [projectAchievements, setProjectAchievements] = useState('');
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  const [milestoneTitle, setMilestoneTitle] = useState('');
  const [milestoneDescription, setMilestoneDescription] = useState('');
  const [milestoneCategory, setMilestoneCategory] = useState('');
  const [milestoneDate, setMilestoneDate] = useState(new Date().toISOString().slice(0, 10));
  const [milestoneLessons, setMilestoneLessons] = useState('');
  const [editingMilestone, setEditingMilestone] = useState<LearningMilestone | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    const [skillResult, projectResult, milestoneResult] = await Promise.all([
      api.getSkills(),
      api.getProjects(),
      api.getMilestones(),
    ]);
    if (!skillResult.success || !projectResult.success || !milestoneResult.success) {
      setError(
        skillResult.error?.message ??
        projectResult.error?.message ??
        milestoneResult.error?.message ??
        'Could not load professional memory.',
      );
    } else {
      setSkills(skillResult.data ?? []);
      setProjects(projectResult.data ?? []);
      setMilestones(milestoneResult.data ?? []);
      setError('');
    }
    setLoading(false);
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const runSearch = async (event: FormEvent) => {
    event.preventDefault();
    const searchText = query.trim();
    if (!searchText) {
      setSearchResults(null);
      return;
    }
    const result = await api.searchMemory(searchText);
    if (!result.success) {
      setError(result.error?.message ?? 'Search failed.');
      return;
    }
    setError('');
    setSearchResults(result.data ?? []);
  };

  const reportMutation = async (success: boolean, message: string, failure: string) => {
    if (!success) {
      setNotice('');
      setError(failure);
      return false;
    }
    setError('');
    setNotice(message);
    await refresh();
    return true;
  };

  const addSkill = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.createSkill({
      name: skillName.trim(),
      proficiency_level: skillTier,
      category: skillCategory.trim() || null,
      evidence_notes: skillEvidence.trim() || null,
      verified_by_project: skillVerified,
    });
    if (await reportMutation(result.success, 'Skill added.', result.error?.message ?? 'Could not add skill.')) {
      setSkillName('');
      setSkillCategory('');
      setSkillEvidence('');
      setSkillVerified(false);
    }
  };

  const saveSkill = async (event: FormEvent) => {
    event.preventDefault();
    if (!editingSkill) return;
    const result = await api.updateSkill(editingSkill.id, {
      name: editingSkill.name,
      proficiency_level: editingSkill.proficiency_level,
      category: editingSkill.category,
      evidence_notes: editingSkill.evidence_notes,
      verified_by_project: editingSkill.verified_by_project,
    });
    if (await reportMutation(result.success, 'Skill updated.', result.error?.message ?? 'Could not update skill.')) {
      setEditingSkill(null);
    }
  };

  const removeSkill = async (skill: Skill) => {
    if (!window.confirm(`Delete “${skill.name}” from memory?`)) return;
    const result = await api.deleteSkill(skill.id);
    await reportMutation(result.success, 'Skill deleted.', result.error?.message ?? 'Could not delete skill.');
  };

  const addProject = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.createProject({
      title: projectTitle.trim(),
      description: projectDescription.trim() || null,
      maturity: projectMaturity,
      github_url: projectGithubUrl.trim() || null,
      repo_name: projectRepoName.trim() || null,
      tech_stack: splitLines(projectTech),
      key_achievements: splitLines(projectAchievements),
      screenshots: [],
    });
    if (await reportMutation(result.success, 'Project added.', result.error?.message ?? 'Could not add project.')) {
      setProjectTitle('');
      setProjectDescription('');
      setProjectGithubUrl('');
      setProjectRepoName('');
      setProjectTech('');
      setProjectAchievements('');
    }
  };

  const saveProject = async (event: FormEvent) => {
    event.preventDefault();
    if (!editingProject) return;
    const result = await api.updateProject(editingProject.id, {
      title: editingProject.title,
      description: editingProject.description,
      maturity: editingProject.maturity,
      github_url: editingProject.github_url?.trim() || null,
      repo_name: editingProject.repo_name?.trim() || null,
      tech_stack: editingProject.tech_stack,
      key_achievements: editingProject.key_achievements,
      screenshots: editingProject.screenshots,
    });
    if (await reportMutation(result.success, 'Project updated.', result.error?.message ?? 'Could not update project.')) {
      setEditingProject(null);
    }
  };

  const removeProject = async (project: Project) => {
    if (!window.confirm(`Delete “${project.title}” from memory?`)) return;
    const result = await api.deleteProject(project.id);
    await reportMutation(result.success, 'Project deleted.', result.error?.message ?? 'Could not delete project.');
  };

  const addMilestone = async (event: FormEvent) => {
    event.preventDefault();
    const result = await api.createMilestone({
      title: milestoneTitle.trim(),
      description: milestoneDescription.trim() || null,
      category: milestoneCategory.trim() || null,
      milestone_date: milestoneDate,
      lessons_learned: milestoneLessons.trim() || null,
    });
    if (await reportMutation(result.success, 'Learning milestone added.', result.error?.message ?? 'Could not add milestone.')) {
      setMilestoneTitle('');
      setMilestoneDescription('');
      setMilestoneCategory('');
      setMilestoneLessons('');
    }
  };

  const saveMilestone = async (event: FormEvent) => {
    event.preventDefault();
    if (!editingMilestone) return;
    const result = await api.updateMilestone(editingMilestone.id, {
      title: editingMilestone.title,
      description: editingMilestone.description,
      category: editingMilestone.category,
      milestone_date: editingMilestone.milestone_date,
      lessons_learned: editingMilestone.lessons_learned,
    });
    if (await reportMutation(result.success, 'Milestone updated.', result.error?.message ?? 'Could not update milestone.')) {
      setEditingMilestone(null);
    }
  };

  const removeMilestone = async (milestone: LearningMilestone) => {
    if (!window.confirm(`Delete “${milestone.title}” from memory?`)) return;
    const result = await api.deleteMilestone(milestone.id);
    await reportMutation(result.success, 'Milestone deleted.', result.error?.message ?? 'Could not delete milestone.');
  };

  const exportMemory = async () => {
    const result = await api.exportMemory();
    if (!result.success || !result.data) {
      setError(result.error?.message ?? 'Could not export professional memory.');
      return;
    }
    const blob = new Blob([JSON.stringify(result.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `professional-memory-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    setError('');
    setNotice('Professional memory exported.');
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header className="flex items-start gap-3 rounded-xl border border-surface-800 bg-surface-900 p-5">
        <BookOpen className="mt-0.5 h-5 w-5 shrink-0 text-brand-400" />
        <div className="flex-1">
          <h2 className="text-sm font-semibold text-slate-100">Professional memory</h2>
          <p className="mt-1 text-xs text-slate-400">Skills, projects, and learning milestones are saved locally and indexed for search.</p>
        </div>
        <button type="button" onClick={() => void exportMemory()} className={buttonClass}><Download className="h-4 w-4" /> Export JSON</button>
      </header>

      <form onSubmit={runSearch} className="flex gap-2 rounded-xl border border-surface-800 bg-surface-900 p-4">
        <input value={query} onChange={(e) => setQuery(e.target.value)} maxLength={200} className={inputClass} placeholder="Search skills, evidence, projects, and lessons…" />
        <button type="submit" className="inline-flex shrink-0 items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500">
          <Search className="h-4 w-4" /> Search
        </button>
        {searchResults !== null && <button type="button" className={buttonClass} onClick={() => { setSearchResults(null); setQuery(''); }}>Clear</button>}
      </form>

      {searchResults !== null && (
        <section className="space-y-2 rounded-xl border border-surface-800 bg-surface-900 p-4">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">Search results ({searchResults.length})</h3>
          {searchResults.length === 0 ? <p className="text-sm text-slate-500">No matching records.</p> : searchResults.map((item) => (
            <article key={`${item.entity_type}-${item.entity_id}`} className="rounded-lg border border-surface-800 bg-surface-950 p-3">
              <div className="text-xs font-semibold capitalize text-brand-300">{item.entity_type.replace('_', ' ')} · {item.title}</div>
              <p className="mt-1 text-xs text-slate-400">{item.snippet}</p>
            </article>
          ))}
        </section>
      )}

      <nav className="flex gap-2 border-b border-surface-800" aria-label="Memory categories">
        {(['skills', 'projects', 'milestones'] as const).map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 text-xs font-medium capitalize ${activeTab === tab ? 'border-b-2 border-brand-500 text-brand-300' : 'text-slate-400 hover:text-slate-200'}`}>
            {tab}
          </button>
        ))}
      </nav>

      {error && <p role="alert" className="rounded-lg border border-rose-800/50 bg-rose-950/30 p-3 text-sm text-rose-300">{error}</p>}
      {notice && <p role="status" className="rounded-lg border border-emerald-800/50 bg-emerald-950/30 p-3 text-sm text-emerald-300">{notice}</p>}
      {loading ? <p className="text-sm text-slate-400">Loading memory…</p> : (
        <>
          {activeTab === 'skills' && (
            <section className="space-y-4">
              <form onSubmit={addSkill} className="grid gap-3 rounded-xl border border-surface-800 bg-surface-900 p-4 md:grid-cols-2">
                <input required maxLength={100} value={skillName} onChange={(e) => setSkillName(e.target.value)} className={inputClass} placeholder="Skill name" />
                <select value={skillTier} onChange={(e) => setSkillTier(e.target.value as SkillTier)} className={inputClass}>
                  <option value="implemented">Implemented</option><option value="studied">Studied</option><option value="explored">Explored</option><option value="discovered">Discovered</option>
                </select>
                <input maxLength={100} value={skillCategory} onChange={(e) => setSkillCategory(e.target.value)} className={inputClass} placeholder="Category (optional)" />
                <input maxLength={4000} value={skillEvidence} onChange={(e) => setSkillEvidence(e.target.value)} className={inputClass} placeholder="Evidence or context (optional)" />
                <label className="flex items-center gap-2 text-xs text-slate-300 md:col-span-2">
                  <input type="checkbox" checked={skillVerified} onChange={(e) => setSkillVerified(e.target.checked)} />
                  Verified by a project
                </label>
                <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 md:col-span-2"><Plus className="h-4 w-4" /> Add skill</button>
              </form>
              {skills.length === 0 && <p className="text-sm text-slate-500">No skills saved yet. Add one above.</p>}
              <div className="grid gap-3 md:grid-cols-2">
                {skills.map((skill) => editingSkill?.id === skill.id ? (
                  <form key={skill.id} onSubmit={saveSkill} className="space-y-2 rounded-xl border border-brand-500/40 bg-surface-900 p-4">
                    <input required className={inputClass} value={editingSkill.name} onChange={(e) => setEditingSkill({ ...editingSkill, name: e.target.value })} />
                    <select className={inputClass} value={editingSkill.proficiency_level} onChange={(e) => setEditingSkill({ ...editingSkill, proficiency_level: e.target.value as SkillTier })}>
                      <option value="implemented">Implemented</option><option value="studied">Studied</option><option value="explored">Explored</option><option value="discovered">Discovered</option>
                    </select>
                    <input className={inputClass} placeholder="Category" value={editingSkill.category ?? ''} onChange={(e) => setEditingSkill({ ...editingSkill, category: e.target.value })} />
                    <textarea className={inputClass} placeholder="Evidence" value={editingSkill.evidence_notes ?? ''} onChange={(e) => setEditingSkill({ ...editingSkill, evidence_notes: e.target.value })} />
                    <label className="flex items-center gap-2 text-xs text-slate-300"><input type="checkbox" checked={editingSkill.verified_by_project} onChange={(e) => setEditingSkill({ ...editingSkill, verified_by_project: e.target.checked })} /> Verified by a project</label>
                    <div className="flex gap-2"><button className={buttonClass}>Save</button><button type="button" onClick={() => setEditingSkill(null)} className={buttonClass}>Cancel</button></div>
                  </form>
                ) : (
                  <article key={skill.id} className="rounded-xl border border-surface-800 bg-surface-900 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div><h3 className="text-sm font-semibold text-slate-100">{skill.name}</h3><span className="mt-1 inline-block rounded bg-brand-500/10 px-2 py-0.5 text-[10px] capitalize text-brand-300">{skill.proficiency_level}</span></div>
                      <div className="flex gap-1"><button aria-label={`Edit ${skill.name}`} onClick={() => setEditingSkill({ ...skill })} className="rounded p-2 text-slate-400 hover:text-slate-100"><Pencil className="h-4 w-4" /></button><button aria-label={`Delete ${skill.name}`} onClick={() => void removeSkill(skill)} className="rounded p-2 text-slate-400 hover:text-rose-300"><Trash2 className="h-4 w-4" /></button></div>
                    </div>
                    {(skill.category || skill.evidence_notes) && <p className="mt-3 text-xs leading-relaxed text-slate-400">{[skill.category, skill.evidence_notes].filter(Boolean).join(' · ')}</p>}
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === 'projects' && (
            <section className="space-y-4">
              <form onSubmit={addProject} className="grid gap-3 rounded-xl border border-surface-800 bg-surface-900 p-4 md:grid-cols-2">
                <input required maxLength={200} value={projectTitle} onChange={(e) => setProjectTitle(e.target.value)} className={inputClass} placeholder="Project title" />
                <select value={projectMaturity} onChange={(e) => setProjectMaturity(e.target.value as ProjectMaturity)} className={inputClass}>
                  <option value="planned">Planned</option><option value="in_development">In development</option><option value="experiment">Experiment</option><option value="learning_exercise">Learning exercise</option><option value="completed">Completed</option>
                </select>
                <textarea value={projectDescription} onChange={(e) => setProjectDescription(e.target.value)} className={`${inputClass} md:col-span-2`} placeholder="Description (optional)" />
                <input maxLength={2000} value={projectGithubUrl} onChange={(e) => setProjectGithubUrl(e.target.value)} className={inputClass} placeholder="GitHub URL (optional)" />
                <input maxLength={200} value={projectRepoName} onChange={(e) => setProjectRepoName(e.target.value)} className={inputClass} placeholder="Repository name (optional)" />
                <textarea value={projectTech} onChange={(e) => setProjectTech(e.target.value)} className={`${inputClass} md:col-span-2`} placeholder="Technologies (one per line)" />
                <textarea value={projectAchievements} onChange={(e) => setProjectAchievements(e.target.value)} className={`${inputClass} md:col-span-2`} placeholder="Verified achievements (one per line)" />
                <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 md:col-span-2"><Plus className="h-4 w-4" /> Add project</button>
              </form>
              {projects.length === 0 && <p className="text-sm text-slate-500">No projects saved yet. Add one above.</p>}
              <div className="space-y-3">
                {projects.map((project) => editingProject?.id === project.id ? (
                  <form key={project.id} onSubmit={saveProject} className="grid gap-2 rounded-xl border border-brand-500/40 bg-surface-900 p-4 md:grid-cols-2">
                    <input required className={inputClass} value={editingProject.title} onChange={(e) => setEditingProject({ ...editingProject, title: e.target.value })} />
                    <select className={inputClass} value={editingProject.maturity} onChange={(e) => setEditingProject({ ...editingProject, maturity: e.target.value as ProjectMaturity })}>
                      <option value="planned">Planned</option><option value="in_development">In development</option><option value="experiment">Experiment</option><option value="learning_exercise">Learning exercise</option><option value="completed">Completed</option>
                    </select>
                    <textarea className={`${inputClass} md:col-span-2`} value={editingProject.description ?? ''} onChange={(e) => setEditingProject({ ...editingProject, description: e.target.value })} />
                    <input className={inputClass} placeholder="GitHub URL" value={editingProject.github_url ?? ''} onChange={(e) => setEditingProject({ ...editingProject, github_url: e.target.value })} />
                    <input className={inputClass} placeholder="Repository name" value={editingProject.repo_name ?? ''} onChange={(e) => setEditingProject({ ...editingProject, repo_name: e.target.value })} />
                    <textarea className={`${inputClass} md:col-span-2`} value={editingProject.tech_stack.join('\n')} onChange={(e) => setEditingProject({ ...editingProject, tech_stack: splitLines(e.target.value) })} placeholder="Technologies (one per line)" />
                    <textarea className={`${inputClass} md:col-span-2`} value={editingProject.key_achievements.join('\n')} onChange={(e) => setEditingProject({ ...editingProject, key_achievements: splitLines(e.target.value) })} placeholder="Verified achievements (one per line)" />
                    <div className="flex gap-2 md:col-span-2"><button className={buttonClass}>Save</button><button type="button" onClick={() => setEditingProject(null)} className={buttonClass}>Cancel</button></div>
                  </form>
                ) : (
                  <article key={project.id} className="rounded-xl border border-surface-800 bg-surface-900 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div><h3 className="text-sm font-semibold text-slate-100">{project.title}</h3><span className="mt-1 inline-block rounded bg-brand-500/10 px-2 py-0.5 text-[10px] capitalize text-brand-300">{project.maturity.replace('_', ' ')}</span></div>
                      <div className="flex gap-1"><button aria-label={`Edit ${project.title}`} onClick={() => setEditingProject({ ...project })} className="rounded p-2 text-slate-400 hover:text-slate-100"><Pencil className="h-4 w-4" /></button><button aria-label={`Delete ${project.title}`} onClick={() => void removeProject(project)} className="rounded p-2 text-slate-400 hover:text-rose-300"><Trash2 className="h-4 w-4" /></button></div>
                    </div>
                    {project.description && <p className="mt-3 text-xs text-slate-400">{project.description}</p>}
                    {project.tech_stack.length > 0 && <p className="mt-2 text-xs text-slate-500">{project.tech_stack.join(' · ')}</p>}
                    {project.github_url && <a className="mt-2 inline-block text-xs text-brand-300 hover:text-brand-200" href={project.github_url} target="_blank" rel="noreferrer">Repository</a>}
                    {project.key_achievements.length > 0 && <ul className="mt-2 list-inside list-disc text-xs text-slate-400">{project.key_achievements.map((achievement) => <li key={achievement}>{achievement}</li>)}</ul>}
                  </article>
                ))}
              </div>
            </section>
          )}

          {activeTab === 'milestones' && (
            <section className="space-y-4">
              <form onSubmit={addMilestone} className="grid gap-3 rounded-xl border border-surface-800 bg-surface-900 p-4 md:grid-cols-2">
                <input required maxLength={200} value={milestoneTitle} onChange={(e) => setMilestoneTitle(e.target.value)} className={inputClass} placeholder="Learning milestone" />
                <input required type="date" value={milestoneDate} onChange={(e) => setMilestoneDate(e.target.value)} className={inputClass} />
                <input maxLength={100} value={milestoneCategory} onChange={(e) => setMilestoneCategory(e.target.value)} className={inputClass} placeholder="Category (optional)" />
                <textarea value={milestoneDescription} onChange={(e) => setMilestoneDescription(e.target.value)} className={inputClass} placeholder="Description (optional)" />
                <textarea value={milestoneLessons} onChange={(e) => setMilestoneLessons(e.target.value)} className={`${inputClass} md:col-span-2`} placeholder="What did you learn?" />
                <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 md:col-span-2"><Plus className="h-4 w-4" /> Add milestone</button>
              </form>
              {milestones.length === 0 && <p className="text-sm text-slate-500">No learning milestones saved yet. Add one above.</p>}
              <div className="space-y-3">
                {milestones.map((milestone) => editingMilestone?.id === milestone.id ? (
                  <form key={milestone.id} onSubmit={saveMilestone} className="grid gap-2 rounded-xl border border-brand-500/40 bg-surface-900 p-4 md:grid-cols-2">
                    <input required className={inputClass} value={editingMilestone.title} onChange={(e) => setEditingMilestone({ ...editingMilestone, title: e.target.value })} />
                    <input required type="date" className={inputClass} value={editingMilestone.milestone_date} onChange={(e) => setEditingMilestone({ ...editingMilestone, milestone_date: e.target.value })} />
                    <input className={inputClass} value={editingMilestone.category ?? ''} onChange={(e) => setEditingMilestone({ ...editingMilestone, category: e.target.value })} placeholder="Category" />
                    <textarea className={inputClass} value={editingMilestone.description ?? ''} onChange={(e) => setEditingMilestone({ ...editingMilestone, description: e.target.value })} placeholder="Description" />
                    <textarea className={`${inputClass} md:col-span-2`} value={editingMilestone.lessons_learned ?? ''} onChange={(e) => setEditingMilestone({ ...editingMilestone, lessons_learned: e.target.value })} placeholder="Lessons learned" />
                    <div className="flex gap-2 md:col-span-2"><button className={buttonClass}>Save</button><button type="button" onClick={() => setEditingMilestone(null)} className={buttonClass}>Cancel</button></div>
                  </form>
                ) : (
                  <article key={milestone.id} className="rounded-xl border border-surface-800 bg-surface-900 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div><h3 className="text-sm font-semibold text-slate-100">{milestone.title}</h3><span className="mt-1 text-[10px] text-slate-500">{milestone.milestone_date}{milestone.category ? ` · ${milestone.category}` : ''}</span></div>
                      <div className="flex gap-1"><button aria-label={`Edit ${milestone.title}`} onClick={() => setEditingMilestone({ ...milestone })} className="rounded p-2 text-slate-400 hover:text-slate-100"><Pencil className="h-4 w-4" /></button><button aria-label={`Delete ${milestone.title}`} onClick={() => void removeMilestone(milestone)} className="rounded p-2 text-slate-400 hover:text-rose-300"><Trash2 className="h-4 w-4" /></button></div>
                    </div>
                    {milestone.description && <p className="mt-3 text-xs text-slate-400">{milestone.description}</p>}
                    {milestone.lessons_learned && <p className="mt-2 text-xs text-slate-300">{milestone.lessons_learned}</p>}
                  </article>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
};
