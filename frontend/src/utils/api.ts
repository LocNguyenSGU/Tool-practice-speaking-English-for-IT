import { getAccessToken, refreshAccessToken } from './auth';

const API_BASE_URL = 'http://localhost:8000';

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * Centralized API call helper with automatic token refresh
 */
export const apiCall = async <T = any>(
  url: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  let token = getAccessToken();

  const makeRequest = async (authToken: string | null) => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    return fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });
  };

  try {
    let response = await makeRequest(token);

    // Auto-refresh on 401 Unauthorized
    if (response.status === 401 && token) {
      const newToken = await refreshAccessToken();
      if (newToken) {
        response = await makeRequest(newToken);
      }
    }

    const status = response.status;

    // Handle different response types
    if (status === 204) {
      return { status, data: undefined as T };
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      
      if (!response.ok) {
        return {
          status,
          error: data.detail || data.message || 'An error occurred',
        };
      }

      return { status, data };
    }

    if (!response.ok) {
      return {
        status,
        error: `Request failed with status ${status}`,
      };
    }

    return { status, data: undefined as T };
  } catch (error) {
    console.error('API call failed:', error);
    return {
      status: 0,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
};

// Convenience methods
export const api = {
  get: <T = any>(url: string) => apiCall<T>(url, { method: 'GET' }),
  
  post: <T = any>(url: string, body?: any) =>
    apiCall<T>(url, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  put: <T = any>(url: string, body?: any) =>
    apiCall<T>(url, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  delete: <T = any>(url: string) => apiCall<T>(url, { method: 'DELETE' }),
};
