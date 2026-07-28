import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { fetchDashboardKPIs, fetchDashboardTrends } from '@/services/dashboardService';
import type { DashboardKPIs, DashboardTrends } from '@/types/dashboard.types';

interface DashboardState {
  kpis: DashboardKPIs | null;
  trends: DashboardTrends | null;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  kpis: null,
  trends: null,
  loading: false,
  error: null,
};

export const getDashboardData = createAsyncThunk(
  'dashboard/getData',
  async (_, { rejectWithValue }) => {
    try {
      const [kpis, trends] = await Promise.all([
        fetchDashboardKPIs(),
        fetchDashboardTrends(),
      ]);
      return { kpis, trends };
    } catch (err: unknown) {
      if (err instanceof Error) {
        return rejectWithValue(err.message);
      }
      return rejectWithValue('Failed to load dashboard data');
    }
  },
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getDashboardData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getDashboardData.fulfilled, (state, action) => {
        state.loading = false;
        state.kpis = action.payload.kpis;
        state.trends = action.payload.trends;
      })
      .addCase(getDashboardData.rejected, (state, action) => {
        state.loading = false;
        state.error = (action.payload as string) || 'Error loading dashboard';
      });
  },
});

export default dashboardSlice.reducer;
