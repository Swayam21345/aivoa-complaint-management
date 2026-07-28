import apiClient from './apiClient';
import type { LoginCredentials, TokenResponse, User } from '@/types/auth.types';

const TOKEN_KEY = 'aiccms_access_token';
const USER_KEY = 'aiccms_user_profile';

export const authService = {
  getStoredToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  getStoredUser(): User | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      localStorage.removeItem(USER_KEY);
      return null;
    }
  },

  async login(credentials: LoginCredentials): Promise<{ user: User; token: string }> {
    // 1. Post credentials to get JWT token
    const tokenRes = await apiClient.post<TokenResponse>('/api/auth/login', credentials);
    const token = tokenRes.data.access_token;
    localStorage.setItem(TOKEN_KEY, token);

    // 2. Fetch current user profile using the new token
    const userRes = await apiClient.get<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const user = userRes.data;
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return { user, token };
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me');
    const user = response.data;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return user;
  },

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

export default authService;
