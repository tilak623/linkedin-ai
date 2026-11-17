import {
  ApiResponse,
  HealthResponse,
  InterviewMode,
  InterviewSession,
  InterviewTurnResult,
  KnowledgeSearchResult,
  LearningMilestone,
  OnboardingInput,
  Project,
  Skill,
  UserAuthStatus,
  UserProfile,
  UserSettings,
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const detail = errorData.detail;
        const validationMessages = Array.isArray(detail)
          ? detail.map((item: unknown) => {
              if (item && typeof item === 'object' && 'msg' in item && typeof item.msg === 'string') {
                return item.msg;
              }
              return '';
            }).filter(Boolean).join('; ')
          : '';
        const message = typeof detail === 'string'
          ? detail
          : validationMessages || (typeof errorData.error?.message === 'string' ? errorData.error.message : response.statusText);
        return {
          success: false,
          data: null,
          error: {
            code: `HTTP_${response.status}`,
            message,
          },
          timestamp: new Date().toISOString(),
        };
      }

      return await response.json();
    } catch (err: unknown) {
      return {
        success: false,
        data: null,
        error: {
          code: 'NETWORK_ERROR',
          message: err instanceof Error ? err.message : 'Unable to connect to backend server. Operating in offline mode.',
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getHealth(): Promise<ApiResponse<HealthResponse>> {
    return this.request<HealthResponse>('/health');
  }

  async getAuthStatus(): Promise<ApiResponse<UserAuthStatus>> {
    return this.request<UserAuthStatus>('/auth/me');
  }

  async getSettings(): Promise<ApiResponse<UserSettings>> {
    return this.request<UserSettings>('/settings');
  }

  async updateSettings(update: Partial<UserSettings>): Promise<ApiResponse<UserSettings>> {
    return this.request<UserSettings>('/settings', {
      method: 'PATCH',
      body: JSON.stringify(update),
    });
  }

  async getProfile(): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/profile');
  }

  async completeOnboarding(input: OnboardingInput): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/profile/onboard', {
      method: 'POST',
      body: JSON.stringify(input),
    });
  }

  async getSkills(): Promise<ApiResponse<Skill[]>> {
    return this.request<Skill[]>('/memory/skills');
  }

  async createSkill(input: Omit<Skill, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Skill>> {
    return this.request<Skill>('/memory/skills', { method: 'POST', body: JSON.stringify(input) });
  }

  async updateSkill(id: string, input: Partial<Omit<Skill, 'id' | 'user_id' | 'created_at' | 'updated_at'>>): Promise<ApiResponse<Skill>> {
    return this.request<Skill>(`/memory/skills/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteSkill(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<{ deleted: boolean }>(`/memory/skills/${encodeURIComponent(id)}`, { method: 'DELETE' });
  }

  async getProjects(): Promise<ApiResponse<Project[]>> {
    return this.request<Project[]>('/memory/projects');
  }

  async createProject(input: Omit<Project, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<Project>> {
    return this.request<Project>('/memory/projects', { method: 'POST', body: JSON.stringify(input) });
  }

  async updateProject(id: string, input: Partial<Omit<Project, 'id' | 'user_id' | 'created_at' | 'updated_at'>>): Promise<ApiResponse<Project>> {
    return this.request<Project>(`/memory/projects/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteProject(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<{ deleted: boolean }>(`/memory/projects/${encodeURIComponent(id)}`, { method: 'DELETE' });
  }

  async getMilestones(): Promise<ApiResponse<LearningMilestone[]>> {
    return this.request<LearningMilestone[]>('/memory/milestones');
  }

  async createMilestone(input: Omit<LearningMilestone, 'id' | 'user_id' | 'created_at'>): Promise<ApiResponse<LearningMilestone>> {
    return this.request<LearningMilestone>('/memory/milestones', { method: 'POST', body: JSON.stringify(input) });
  }

  async updateMilestone(id: string, input: Partial<Omit<LearningMilestone, 'id' | 'user_id' | 'created_at'>>): Promise<ApiResponse<LearningMilestone>> {
    return this.request<LearningMilestone>(`/memory/milestones/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteMilestone(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
    return this.request<{ deleted: boolean }>(`/memory/milestones/${encodeURIComponent(id)}`, { method: 'DELETE' });
  }

  async searchMemory(query: string): Promise<ApiResponse<KnowledgeSearchResult[]>> {
    return this.request<KnowledgeSearchResult[]>(`/memory/search?q=${encodeURIComponent(query)}`);
  }

  async exportMemory(): Promise<ApiResponse<Record<string, unknown>>> {
    return this.request<Record<string, unknown>>('/memory/export');
  }

  async getTodayInterview(): Promise<ApiResponse<InterviewSession | null>> {
    return this.request<InterviewSession | null>('/interviews/today');
  }

  async startInterview(mode: InterviewMode): Promise<ApiResponse<InterviewSession>> {
    return this.request<InterviewSession>('/interviews/start', {
      method: 'POST',
      body: JSON.stringify({ mode }),
    });
  }

  async submitInterviewTurn(id: string, userResponse: string): Promise<ApiResponse<InterviewTurnResult>> {
    return this.request<InterviewTurnResult>(`/interviews/${encodeURIComponent(id)}/turn`, {
      method: 'POST',
      body: JSON.stringify({ user_response: userResponse }),
    });
  }

  async completeInterview(id: string): Promise<ApiResponse<InterviewSession>> {
    return this.request<InterviewSession>(`/interviews/${encodeURIComponent(id)}/complete`, { method: 'POST' });
  }
}

export const api = new ApiService();
