export type WorkspaceView =
  | 'home'
  | 'interview'
  | 'content'
  | 'media'
  | 'calendar'
  | 'research'
  | 'memory'
  | 'portfolio'
  | 'networking'
  | 'analytics'
  | 'profile'
  | 'settings';

export interface SystemResourceInfo {
  cpu_cores: number;
  total_ram_gb: number;
  available_ram_gb: number;
  free_disk_gb: number;
  os_name: string;
  python_version: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'disconnected';
  environment: string;
  version: string;
  database: string;
  ai_provider: string;
  resources: SystemResourceInfo;
}

export interface UserSettings {
  id: string;
  user_id: string;
  theme: 'dark' | 'light' | 'system';
  reminder_interval_mins: number;
  reminders_enabled: boolean;
  preferred_ai_provider: 'gemini' | 'groq' | 'local';
  offline_mode: boolean;
  github_username: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  user_id: string;
  headline: string | null;
  summary: string | null;
  career_direction: string | null;
  target_audience: string | null;
  writing_voice_notes: string | null;
  seniority_level: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserAuthStatus {
  authenticated: boolean;
  user_id: string;
  email: string;
  full_name: string;
  onboarding_completed: boolean;
  profile: UserProfile | null;
  settings: UserSettings | null;
}

export type SkillTier = 'implemented' | 'studied' | 'explored' | 'discovered';
export type ProjectMaturity = 'completed' | 'in_development' | 'experiment' | 'learning_exercise' | 'planned';

export interface Skill {
  id: string;
  user_id: string;
  name: string;
  proficiency_level: SkillTier;
  category: string | null;
  verified_by_project: boolean;
  evidence_notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  maturity: ProjectMaturity;
  github_url: string | null;
  repo_name: string | null;
  tech_stack: string[];
  key_achievements: string[];
  screenshots: string[];
  created_at: string;
  updated_at: string;
}

export interface LearningMilestone {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  category: string | null;
  milestone_date: string;
  lessons_learned: string | null;
  created_at: string;
}

export interface KnowledgeSearchResult {
  entity_type: string;
  entity_id: string;
  title: string;
  snippet: string;
}

export interface OnboardingInput {
  full_name: string;
  headline: string | null;
  summary: string | null;
  career_direction: string | null;
  target_audience: string | null;
  writing_voice_notes: string | null;
  seniority_level: string | null;
  initial_skills: Array<{
    name: string;
    proficiency_level: SkillTier;
    category: string | null;
    evidence_notes: string | null;
    verified_by_project: boolean;
  }>;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: string;
}
