import { ApiResponse, HealthResponse, UserAuthStatus, UserSettings } from '../types';

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
        return {
          success: false,
          data: null,
          error: {
            code: `HTTP_${response.status}`,
            message: errorData.detail || errorData.error?.message || response.statusText,
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
}

export const api = new ApiService();
