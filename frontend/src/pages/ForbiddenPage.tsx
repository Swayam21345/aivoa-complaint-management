import { Link } from 'react-router-dom';

export function UnauthorizedPage() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 bg-amber-50 rounded-full flex items-center justify-center text-amber-600 mb-4 border border-amber-200">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">401 - Authentication Required</h1>
      <p className="text-sm text-gray-600 max-w-md mb-6">
        Your session has expired or you are not signed in. Please log in to access this pharmaceutical workspace.
      </p>
      <Link
        to="/login"
        className="px-4 py-2 text-xs font-semibold text-white bg-primary-600 hover:bg-primary-700 rounded-lg shadow-xs transition-colors"
      >
        Go to Login
      </Link>
    </div>
  );
}

export function ForbiddenPage() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-600 mb-4 border border-red-200">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">403 - Access Forbidden</h1>
      <p className="text-sm text-gray-600 max-w-md mb-6">
        You do not have the required role or privileges to access this page or perform this action.
      </p>
      <Link
        to="/"
        className="px-4 py-2 text-xs font-semibold text-white bg-primary-600 hover:bg-primary-700 rounded-lg shadow-xs transition-colors"
      >
        Return to Dashboard
      </Link>
    </div>
  );
}

export default ForbiddenPage;
