// Token management utilities

const TOKEN_KEY = 'vi_en_token';
const REFRESH_KEY = 'vi_en_refresh';
const USER_KEY = 'vi_en_user';

interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Store tokens
export const storeTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
};

// Get access token
export const getAccessToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

// Get refresh token
export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_KEY);
};

// Store user data
export const storeUser = (user: User) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

// Get user data
export const getUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

// Clear all auth data
export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

// Refresh access token
export const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearAuth();
      return null;
    }

    const data: TokenResponse = await response.json();
    storeTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearAuth();
    return null;
  }
};

// Auto-refresh token 5 minutes before expiry
export const setupTokenRefresh = (expiresIn: number) => {
  const refreshTime = (expiresIn - 300) * 1000; // 5 minutes before expiry
  setTimeout(() => {
    refreshAccessToken().then((newToken) => {
      if (newToken) {
        // Setup next refresh
        setupTokenRefresh(expiresIn);
      }
    });
  }, refreshTime);
};

// Logout
export const logout = () => {
  clearAuth();
  window.location.href = '/';
};
