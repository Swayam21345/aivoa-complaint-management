import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { loginUser, clearAuthError } from '@/store/slices/authSlice';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { isAuthenticated, loading, error } = useAppSelector(
    (state) => state.auth,
  );

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState('');

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  useEffect(() => {
    dispatch(clearAuthError());
  }, [dispatch]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');

    if (!email.trim()) {
      setValidationError('Please enter your email address.');
      return;
    }
    if (!password) {
      setValidationError('Please enter your password.');
      return;
    }

    const result = await dispatch(
      loginUser({ email: email.trim(), password }),
    );

    if (loginUser.fulfilled.match(result)) {
      navigate(from, { replace: true });
    }
  };

  const setDemoCredentials = (roleEmail: string, rolePass: string) => {
    setEmail(roleEmail);
    setPassword(rolePass);
    setValidationError('');
    dispatch(clearAuthError());
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        {/* Brand Logo */}
        <div className="inline-flex items-center justify-center gap-3 mb-3">
          <svg className="w-10 h-10 shrink-0" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#1A56DB" />
            <path
              d="M8 10h16M8 16h10M8 22h12"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <circle cx="24" cy="22" r="4" fill="#057A55" />
          </svg>
          <div className="text-left">
            <h1 className="text-2xl font-black tracking-tight text-gray-900 leading-none">
              AICCMS <span className="text-primary-600 font-medium text-lg">QMS</span>
            </h1>
            <p className="text-xs text-gray-500 font-medium">
              Pharma Quality Control System
            </p>
          </div>
        </div>

        <h2 className="text-xl font-bold text-gray-900 tracking-tight">
          Sign in to your account
        </h2>
        <p className="mt-1 text-xs text-gray-600">
          Access AI Complaint Management & Audit Portal
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-sm border border-gray-200 sm:rounded-xl sm:px-8">
          {/* Error Banner */}
          {(error || validationError) && (
            <div className="mb-4 rounded-md bg-red-50 p-3.5 border border-red-200">
              <div className="flex items-start gap-2.5">
                <svg
                  className="w-5 h-5 text-red-600 shrink-0 mt-0.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div className="text-xs text-red-700 font-medium">
                  {validationError || error}
                </div>
              </div>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold text-gray-700 mb-1"
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. admin@aiccms.local"
                className="w-full px-3.5 py-2.5 text-xs rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-xs font-semibold text-gray-700 mb-1"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 text-xs rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 text-xs font-semibold rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 transition-colors shadow-xs flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign In</span>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Assistant */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider text-center mb-2.5">
              Default Demo Roles
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() =>
                  setDemoCredentials('admin@aiccms.local', 'Admin@123')
                }
                className="px-2.5 py-1.5 text-[11px] font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors text-left"
              >
                <div className="font-semibold text-primary-700">👑 Admin</div>
                <div className="text-[10px] text-gray-400">admin@aiccms.local</div>
              </button>
              <button
                type="button"
                onClick={() =>
                  setDemoCredentials('qa@aiccms.local', 'QAManager@123')
                }
                className="px-2.5 py-1.5 text-[11px] font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors text-left"
              >
                <div className="font-semibold text-emerald-700">🛡️ QA Manager</div>
                <div className="text-[10px] text-gray-400">qa@aiccms.local</div>
              </button>
              <button
                type="button"
                onClick={() =>
                  setDemoCredentials('investigator@aiccms.local', 'Investigator@123')
                }
                className="px-2.5 py-1.5 text-[11px] font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors text-left"
              >
                <div className="font-semibold text-indigo-700">🔍 Investigator</div>
                <div className="text-[10px] text-gray-400">investigator@aiccms.local</div>
              </button>
              <button
                type="button"
                onClick={() =>
                  setDemoCredentials('viewer@aiccms.local', 'Viewer@123')
                }
                className="px-2.5 py-1.5 text-[11px] font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-md transition-colors text-left"
              >
                <div className="font-semibold text-gray-700">👁️ Viewer</div>
                <div className="text-[10px] text-gray-400">viewer@aiccms.local</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
