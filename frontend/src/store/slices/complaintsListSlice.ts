import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { listComplaints } from '@/services/complaintService';
import type { ListComplaintsParams } from '@/services/complaintService';
import type { PaginatedComplaints, ComplaintListItem } from '@/types/complaint.types';

// ─── Thunks ───────────────────────────────────────────────────────────────────

export const fetchComplaints = createAsyncThunk<
  PaginatedComplaints,
  ListComplaintsParams,
  { rejectValue: string }
>('complaintsList/fetch', async (params, { rejectWithValue }) => {
  try {
    return await listComplaints(params);
  } catch (error) {
    return rejectWithValue((error as Error).message);
  }
});

// ─── State ────────────────────────────────────────────────────────────────────

interface Filters {
  status: string;
  risk_level: string;
  priority: string;
  category: string;
  search: string;
  sort: 'created_at_asc' | 'created_at_desc';
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

interface ComplaintsListState {
  items: ComplaintListItem[];
  total: number;
  page: number;
  page_size: number;
  filters: Filters;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: ComplaintsListState = {
  items: [],
  total: 0,
  page: 1,
  page_size: 20,
  filters: {
    status: '',
    risk_level: '',
    priority: '',
    category: '',
    search: '',
    sort: 'created_at_desc',
    sort_by: 'created_at',
    sort_order: 'desc',
  },
  status: 'idle',
  error: null,
};

// ─── Slice ────────────────────────────────────────────────────────────────────

const complaintsListSlice = createSlice({
  name: 'complaintsList',
  initialState,
  reducers: {
    setFilter(
      state,
      action: PayloadAction<{ key: keyof Filters; value: string }>,
    ) {
      // Cast is safe — the thunk re-fetches with the updated value
      (state.filters as Record<string, string>)[action.payload.key] =
        action.payload.value;
      state.page = 1; // reset to first page on filter change
    },
    setPage(state, action: PayloadAction<number>) {
      state.page = action.payload;
    },
    resetFilters(state) {
      state.filters = initialState.filters;
      state.page = 1;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload.items;
        state.total = action.payload.total;
        state.page = action.payload.page;
        state.page_size = action.payload.page_size;
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload ?? 'Failed to load complaints.';
      });
  },
});

export const { setFilter, setPage, resetFilters } = complaintsListSlice.actions;

export default complaintsListSlice.reducer;
