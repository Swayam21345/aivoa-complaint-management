import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { logoutUser } from '@/store/slices/authSlice';
import type { UserRole } from '@/types/auth.types';

export default function Navbar() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated, role } = useAppSelector((state) => state.auth);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await dispatch(logoutUser());
    navigate('/login', { replace: true });
  };

  const getRoleBadgeColor = (userRole?: UserRole | null) => {
    switch (userRole) {
      case 'ADMIN':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'QA_MANAGER':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'INVESTIGATOR':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'VIEWER':
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getInitials = (name?: string) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const canUpload = role && ['ADMIN', 'QA_MANAGER', 'INVESTIGATOR'].includes(role);
  const showReports = role && ['ADMIN', 'QA_MANAGER'].includes(role);
  const showAdminNav = role === 'ADMIN';

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-xs">
      <nav
        className="mx-auto max-w-screen-xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between"
        aria-label="Main navigation"
      >
        {/* Logo / brand */}
        <Link
          to="/"
          className="flex items-center gap-2.5 text-primary-700 font-bold text-base no-underline hover:text-primary-800"
          aria-label="AICCMS — go to executive dashboard"
        >
          <svg
            className="w-8 h-8 shrink-0"
            viewBox="0 0 32 32"
            fill="none"
            aria-hidden="true"
          >
            <rect width="32" height="32" rx="8" fill="#1A56DB" />
            <path
              d="M8 10h16M8 16h10M8 22h12"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <circle cx="24" cy="22" r="4" fill="#057A55" />
          </svg>
          <div className="flex flex-col">
            <span className="tracking-tight leading-none text-gray-900 font-extrabold text-sm">
              AICCMS <span className="text-xs font-normal text-primary-600">QMS</span>
            </span>
            <span className="text-[10px] font-medium text-gray-400 leading-tight">
              Pharma Quality Control
            </span>
          </div>
        </Link>

        {/* Nav links & Profile */}
        <div className="flex items-center gap-2">
          {isAuthenticated && (
            <>
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                📊 Dashboard
              </NavLink>

              <NavLink
                to="/complaints"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                📋 Complaints
              </NavLink>

              <NavLink
                to="/capa"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                🛡️ CAPA
              </NavLink>

              <NavLink
                to="/rca"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                🔬 RCA
              </NavLink>

              <NavLink
                to="/documents"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                📁 Documents
              </NavLink>

              <NavLink
                to="/training"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                🎓 Training
              </NavLink>

              <NavLink
                to="/competency"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                🏅 Competencies
              </NavLink>

              <NavLink
                to="/suppliers"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                🏭 Suppliers
              </NavLink>

              <NavLink
                to="/internal-audits"
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`
                }
              >
                📋 Internal Audits
              </NavLink>







              {canUpload && (
                <NavLink
                  to="/upload"
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md text-xs font-medium transition-colors no-underline ${
                      isActive
                        ? 'bg-primary-50 text-primary-700 font-semibold'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`
                  }
                >
                  📄 Upload & AI
                </NavLink>
              )}

              {showReports && (
                <span className="px-2 py-1 text-[11px] font-medium text-gray-400 cursor-not-allowed hidden md:inline">
                  📈 Reports
                </span>
              )}

              {showAdminNav && (
                <span className="px-2 py-1 text-[11px] font-medium text-gray-400 cursor-not-allowed hidden md:inline">
                  ⚙️ Admin
                </span>
              )}

              {canUpload && (
                <Link
                  to="/upload"
                  className="btn-primary ml-1 text-xs py-1.5 px-3 no-underline shadow-xs flex items-center gap-1"
                >
                  <span>✦</span>
                  <span>+ New Complaint</span>
                </Link>
              )}
            </>
          )}

          {/* User Profile Dropdown or Sign In */}
          {isAuthenticated && user ? (
            <div className="relative ml-2" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setDropdownOpen((prev) => !prev)}
                className="flex items-center gap-2 p-1 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
                aria-expanded={dropdownOpen}
                aria-label="User menu"
              >
                <div className="w-8 h-8 rounded-full bg-primary-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                  {getInitials(user.full_name)}
                </div>
                <svg
                  className={`w-4 h-4 text-gray-500 transition-transform ${
                    dropdownOpen ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-xs font-bold text-gray-900 truncate">
                      {user.full_name}
                    </p>
                    <p className="text-[11px] text-gray-500 truncate mb-1.5">
                      {user.email}
                    </p>
                    <span
                      className={`inline-block px-2 py-0.5 text-[10px] font-semibold rounded-full border ${getRoleBadgeColor(
                        user.role,
                      )}`}
                    >
                      {user.role}
                    </span>
                  </div>

                  <div className="py-1">
                    <button
                      type="button"
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-xs font-medium text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                        />
                      </svg>
                      Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              className="ml-2 text-xs font-semibold px-3 py-1.5 bg-primary-600 text-white hover:bg-primary-700 rounded-lg no-underline transition-colors shadow-xs"
            >
              Sign In
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
