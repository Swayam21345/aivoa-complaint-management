import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import authService from './authService';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60_000, // 60 s — AI processing can take up to 30 s
});

// ─── Request interceptor ──────────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getStoredToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error),
);

// ─── Response interceptor ────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      const isLoginRequest = error.config?.url?.includes('/api/auth/login');
      if (!isLoginRequest) {
        authService.logout();
        // Dispatch session-expired event if needed or allow app auth listener to handle
        window.dispatchEvent(new Event('auth:unauthorized'));
      }
    }

    // Normalise error shape so components receive a consistent message
    const message =
      (error.response?.data as { detail?: string })?.detail ??
      error.message ??
      'An unexpected error occurred.';
    return Promise.reject(new Error(message));
  },
);

export default apiClient;
