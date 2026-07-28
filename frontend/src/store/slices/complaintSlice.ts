import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import { createComplaint, getComplaint, updateComplaint } from '@/services/complaintService';
import type { CreateComplaintRequest, UpdateComplaintRequest } from '@/types/api.types';
import type { AIAnalysis, ComplaintDetail, ComplaintFormDraft } from '@/types/complaint.types';

// ─── Thunks ───────────────────────────────────────────────────────────────────

export const submitComplaint = createAsyncThunk<
  { complaint_id: string; id: string },
  CreateComplaintRequest,
  { rejectValue: string }
>('complaint/submit', async (data, { rejectWithValue }) => {
  try {
    const res = await createComplaint(data);
    return { complaint_id: res.complaint_id, id: res.id };
  } catch (error) {
    return rejectWithValue((error as Error).message);
  }
});

export const fetchComplaintDetail = createAsyncThunk<
  ComplaintDetail,
  string,
  { rejectValue: string }
>('complaint/fetchDetail', async (id, { rejectWithValue }) => {
  try {
    return await getComplaint(id);
  } catch (error) {
    return rejectWithValue((error as Error).message);
  }
});

export const patchComplaintStatus = createAsyncThunk<
  { id: string; status: string; updated_at: string },
  { id: string; data: UpdateComplaintRequest },
  { rejectValue: string }
>('complaint/patchStatus', async ({ id, data }, { rejectWithValue }) => {
  try {
    const res = await updateComplaint(id, data);
    return { id: res.id, status: res.status, updated_at: res.updated_at };
  } catch (error) {
    return rejectWithValue((error as Error).message);
  }
});

// ─── State ────────────────────────────────────────────────────────────────────

interface ComplaintState {
  // Active form draft (populated by AI or user edits)
  draft: ComplaintFormDraft;
  // AI analysis result attached to the draft
  aiAnalysis: AIAnalysis | null;
  // Submission lifecycle
  submitStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
  submittedId: string | null;
  submittedComplaintId: string | null;
  // Detail view
  detail: ComplaintDetail | null;
  detailStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
  // Shared error
  error: string | null;
}

const emptyDraft: ComplaintFormDraft = {
  product_name: '',
  batch_number: '',
  customer_name: '',
  category: '',
  risk_level: '',
  complaint_text: '',
  reviewer_notes: '',
  submitted_by: '',
  date_received: new Date().toISOString().split('T')[0],
};

const initialState: ComplaintState = {
  draft: emptyDraft,
  aiAnalysis: null,
  submitStatus: 'idle',
  submittedId: null,
  submittedComplaintId: null,
  detail: null,
  detailStatus: 'idle',
  error: null,
};

// ─── Slice ────────────────────────────────────────────────────────────────────

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    /** Populate the draft form from AI analysis results */
    populateDraftFromAI(state, action: PayloadAction<AIAnalysis>) {
      const ai = action.payload;
      state.aiAnalysis = ai;
      state.draft = {
        ...state.draft,
        product_name: ai.product_name ?? '',
        batch_number: ai.batch_number ?? '',
        customer_name: ai.customer_name ?? '',
        category: ai.category ?? '',
        risk_level: ai.risk_level ?? '',
        complaint_text: ai.complaint_summary ?? '',
      };
    },
    /** Update a single draft field when the user edits the form */
    updateDraftField<K extends keyof ComplaintFormDraft>(
      state: ComplaintState,
      action: PayloadAction<{ field: K; value: ComplaintFormDraft[K] }>,
    ) {
      state.draft[action.payload.field] = action.payload.value;
    },
    /** Reset the form and AI state (e.g., after successful submit) */
    resetComplaintForm(state) {
      state.draft = emptyDraft;
      state.aiAnalysis = null;
      state.submitStatus = 'idle';
      state.submittedId = null;
      state.submittedComplaintId = null;
      state.error = null;
    },
    clearComplaintError(state) {
      state.error = null;
    },
    clearDetail(state) {
      state.detail = null;
      state.detailStatus = 'idle';
    },
  },
  extraReducers: (builder) => {
    // ── submit ──────────────────────────────────────────────────────────────
    builder
      .addCase(submitComplaint.pending, (state) => {
        state.submitStatus = 'loading';
        state.error = null;
      })
      .addCase(submitComplaint.fulfilled, (state, action) => {
        state.submitStatus = 'succeeded';
        state.submittedId = action.payload.id;
        state.submittedComplaintId = action.payload.complaint_id;
      })
      .addCase(submitComplaint.rejected, (state, action) => {
        state.submitStatus = 'failed';
        state.error = action.payload ?? 'Submission failed.';
      });

    // ── fetchDetail ─────────────────────────────────────────────────────────
    builder
      .addCase(fetchComplaintDetail.pending, (state) => {
        state.detailStatus = 'loading';
        state.error = null;
      })
      .addCase(fetchComplaintDetail.fulfilled, (state, action) => {
        state.detailStatus = 'succeeded';
        state.detail = action.payload;
      })
      .addCase(fetchComplaintDetail.rejected, (state, action) => {
        state.detailStatus = 'failed';
        state.error = action.payload ?? 'Failed to load complaint.';
      });

    // ── patchStatus ─────────────────────────────────────────────────────────
    builder.addCase(patchComplaintStatus.fulfilled, (state, action) => {
      if (state.detail && state.detail.id === action.payload.id) {
        state.detail.status = action.payload.status as ComplaintDetail['status'];
        state.detail.updated_at = action.payload.updated_at;
      }
    });
  },
});

export const {
  populateDraftFromAI,
  updateDraftField,
  resetComplaintForm,
  clearComplaintError,
  clearDetail,
} = complaintSlice.actions;

export default complaintSlice.reducer;
