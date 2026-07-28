import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy, useEffect } from 'react';

import Navbar from '@/components/layout/Navbar/Navbar';
import ToastContainer from '@/components/common/Toast/ToastContainer';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import NotFoundPage from '@/pages/NotFoundPage';
import { UnauthorizedPage, ForbiddenPage } from '@/pages/ForbiddenPage';
import { useAppDispatch } from '@/store/hooks';
import { restoreSession, logoutUser } from '@/store/slices/authSlice';

// ─── Lazy-loaded page components ──────────────────────────────────────────────
const LoginPage = lazy(() => import('@/pages/LoginPage/LoginPage'));
const DashboardPage = lazy(
  () => import('@/pages/DashboardPage/DashboardPage'),
);
const UploadPage = lazy(() => import('@/pages/UploadPage/UploadPage'));
const ComplaintFormPage = lazy(
  () => import('@/pages/ComplaintFormPage/ComplaintFormPage'),
);
const ComplaintsListPage = lazy(
  () => import('@/pages/ComplaintsListPage/ComplaintsListPage'),
);
const ComplaintDetailPage = lazy(
  () => import('@/pages/ComplaintDetailPage/ComplaintDetailPage'),
);

const CAPAListPage = lazy(() => import('@/pages/CAPAListPage/CAPAListPage'));
const CAPADetailPage = lazy(() => import('@/pages/CAPADetailPage/CAPADetailPage'));

const RCAListPage = lazy(() => import('@/pages/RCAListPage/RCAListPage'));
const RCADetailPage = lazy(() => import('@/pages/RCADetailPage/RCADetailPage'));

const DocumentLibraryPage = lazy(() => import('@/pages/DocumentLibraryPage/DocumentLibraryPage'));
const DocumentDetailPage = lazy(() => import('@/pages/DocumentDetailPage/DocumentDetailPage'));

const TrainingPage = lazy(() => import('@/pages/TrainingPage/TrainingPage'));
const TrainingDetailPage = lazy(() => import('@/pages/TrainingDetailPage/TrainingDetailPage'));
const CompetencyPage = lazy(() => import('@/pages/CompetencyPage/CompetencyPage'));

const SupplierPage = lazy(() => import('@/pages/SupplierPage/SupplierPage'));
const SupplierDetailPage = lazy(() => import('@/pages/SupplierDetailPage/SupplierDetailPage'));
const SupplierDashboardPage = lazy(() => import('@/pages/SupplierDashboardPage/SupplierDashboardPage'));

const InternalAuditPage = lazy(() => import('@/pages/InternalAuditPage/InternalAuditPage'));
const InternalAuditDetailPage = lazy(() => import('@/pages/InternalAuditDetailPage/InternalAuditDetailPage'));
const InternalAuditDashboardPage = lazy(() => import('@/pages/InternalAuditDashboardPage/InternalAuditDashboardPage'));






// ─── Global loading fallback ──────────────────────────────────────────────────
function PageFallback() {
  return (
    <div
      className="flex items-center justify-center min-h-[60vh]"
      aria-live="polite"
      aria-label="Loading page"
    >
      <div className="w-8 h-8 rounded-full border-4 border-primary-200 border-t-primary-600 animate-spin" />
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Restore session on app load
    dispatch(restoreSession());

    // Catch 401 unauthorized events emitted from apiClient
    const handleUnauthorized = () => {
      dispatch(logoutUser());
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [dispatch]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      <Suspense fallback={<PageFallback />}>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          <Route path="/forbidden" element={<ForbiddenPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            {/* Dashboard: All roles */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<Navigate to="/" replace />} />

            {/* Complaints List & Detail: All roles */}
            <Route path="/complaints" element={<ComplaintsListPage />} />
            <Route path="/complaints/:id" element={<ComplaintDetailPage />} />

            {/* CAPA Module: All roles */}
            <Route path="/capa" element={<CAPAListPage />} />
            <Route path="/capa/:id" element={<CAPADetailPage />} />

            {/* RCA Module: All roles */}
            <Route path="/rca" element={<RCAListPage />} />
            <Route path="/rca/:id" element={<RCADetailPage />} />

            {/* Document Module: All roles */}
            <Route path="/documents" element={<DocumentLibraryPage />} />
            <Route path="/documents/:id" element={<DocumentDetailPage />} />

            {/* Training Module: All roles */}
            <Route path="/training" element={<TrainingPage />} />
            <Route path="/training/:id" element={<TrainingDetailPage />} />
            <Route path="/competency" element={<CompetencyPage />} />

            {/* Supplier Quality Management Module: All roles */}
            <Route path="/suppliers" element={<SupplierPage />} />
            <Route path="/suppliers/dashboard" element={<SupplierDashboardPage />} />
            <Route path="/suppliers/:id" element={<SupplierDetailPage />} />

            {/* Internal Audit & Inspection Readiness Module: All roles */}
            <Route path="/internal-audits" element={<InternalAuditPage />} />
            <Route path="/internal-audits/dashboard" element={<InternalAuditDashboardPage />} />
            <Route path="/internal-audits/:id" element={<InternalAuditDetailPage />} />






            {/* Upload & Form: ADMIN, QA_MANAGER, INVESTIGATOR */}
            <Route
              element={
                <ProtectedRoute
                  allowedRoles={['ADMIN', 'QA_MANAGER', 'INVESTIGATOR']}
                />
              }
            >
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/complaint/new" element={<ComplaintFormPage />} />
            </Route>
          </Route>


          {/* Legacy root redirect */}
          <Route path="/home" element={<Navigate to="/" replace />} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>

      <ToastContainer />
    </div>
  );
}
