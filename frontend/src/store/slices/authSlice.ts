import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import authService from '@/services/authService';
import type { AuthState, LoginCredentials, User, UserRole } from '@/types/auth.types';

const initialToken = authService.getStoredToken();
const initialUser = authService.getStoredUser();

const initialState: AuthState = {
  user: initialUser,
  token: initialToken,
  role: initialUser?.role ?? null,
  isAuthenticated: Boolean(initialToken && initialUser),
  loading: false,
  error: null,
};

// ─── Async Thunks ─────────────────────────────────────────────────────────────

export const loginUser = createAsyncThunk<
  { user: User; token: string },
  LoginCredentials,
  { rejectValue: string }
>('auth/loginUser', async (credentials, { rejectWithValue }) => {
  try {
    return await authService.login(credentials);
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Invalid email or password';
    return rejectWithValue(msg);
  }
});

export const fetchCurrentUser = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>('auth/fetchCurrentUser', async (_, { rejectWithValue }) => {
  try {
    return await authService.getCurrentUser();
  } catch (error) {
    const msg = error instanceof Error ? error.message : 'Failed to fetch user profile';
    return rejectWithValue(msg);
  }
});

export const restoreSession = createAsyncThunk<
  { user: User | null; token: string | null },
  void
>('auth/restoreSession', async () => {
  const token = authService.getStoredToken();
  const storedUser = authService.getStoredUser();

  if (!token) {
    authService.logout();
    return { user: null, token: null };
  }

  try {
    const freshUser = await authService.getCurrentUser();
    return { user: freshUser, token };
  } catch {
    // If token validation fails, revert to stored user if offline or clean session
    if (storedUser) {
      return { user: storedUser, token };
    }
    authService.logout();
    return { user: null, token: null };
  }
});

export const logoutUser = createAsyncThunk('auth/logoutUser', async () => {
  authService.logout();
});

// ─── Slice ────────────────────────────────────────────────────────────────────

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearAuthError: (state) => {
      state.error = null;
    },
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string }>,
    ) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.role = action.payload.user.role;
      state.isAuthenticated = true;
      state.loading = false;
      state.error = null;
    },
    logout: (state) => {
      authService.logout();
      state.user = null;
      state.token = null;
      state.role = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder.addCase(loginUser.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(loginUser.fulfilled, (state, action) => {
      state.loading = false;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.role = action.payload.user.role;
      state.isAuthenticated = true;
      state.error = null;
    });
    builder.addCase(loginUser.rejected, (state, action) => {
      state.loading = false;
      state.error = action.payload ?? 'Login failed';
      state.isAuthenticated = false;
    });

    // Fetch Current User
    builder.addCase(fetchCurrentUser.fulfilled, (state, action) => {
      state.user = action.payload;
      state.role = action.payload.role;
      state.isAuthenticated = true;
    });
    builder.addCase(fetchCurrentUser.rejected, (state) => {
      state.user = null;
      state.token = null;
      state.role = null;
      state.isAuthenticated = false;
    });

    // Restore Session
    builder.addCase(restoreSession.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(restoreSession.fulfilled, (state, action) => {
      state.loading = false;
      state.user = action.payload.user;
      state.token = action.payload.token;
      state.role = action.payload.user?.role ?? null as UserRole | null;
      state.isAuthenticated = Boolean(action.payload.token && action.payload.user);
    });
    builder.addCase(restoreSession.rejected, (state) => {
      state.loading = false;
      state.user = null;
      state.token = null;
      state.role = null;
      state.isAuthenticated = false;
    });

    // Logout
    builder.addCase(logoutUser.fulfilled, (state) => {
      state.user = null;
      state.token = null;
      state.role = null;
      state.isAuthenticated = false;
      state.loading = false;
      state.error = null;
    });
  },
});

export const { clearAuthError, setCredentials, logout } = authSlice.actions;

export default authSlice.reducer;
