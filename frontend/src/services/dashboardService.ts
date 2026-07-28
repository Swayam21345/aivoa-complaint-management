import apiClient from './apiClient';
import type { DashboardKPIs, DashboardTrends } from '@/types/dashboard.types';

export async function fetchDashboardKPIs(): Promise<DashboardKPIs> {
  const response = await apiClient.get<DashboardKPIs>('/api/dashboard');
  return response.data;
}

export async function fetchDashboardTrends(): Promise<DashboardTrends> {
  const response = await apiClient.get<DashboardTrends>('/api/dashboard/trends');
  return response.data;
}
