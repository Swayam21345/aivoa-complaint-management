import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import uploadReducer from './slices/uploadSlice';
import complaintReducer from './slices/complaintSlice';
import complaintsListReducer from './slices/complaintsListSlice';
import dashboardReducer from './slices/dashboardSlice';
import toastReducer from './slices/toastSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    upload: uploadReducer,
    complaint: complaintReducer,
    complaintsList: complaintsListReducer,
    dashboard: dashboardReducer,
    toast: toastReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      // File objects are not serializable — we store only metadata in Redux,
      // but relax the check for the upload slice which is transient state.
      serializableCheck: {
        ignoredPaths: ['upload.selectedFile'],
      },
    }),
  devTools: import.meta.env.DEV,
});

// ─── Typed hooks ──────────────────────────────────────────────────────────────

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
