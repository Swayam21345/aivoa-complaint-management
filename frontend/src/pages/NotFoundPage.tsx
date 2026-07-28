import { Link } from 'react-router-dom';
import PageContainer from '@/components/layout/PageContainer/PageContainer';

export default function NotFoundPage() {
  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <p className="text-6xl font-bold text-gray-200 mb-4">404</p>
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Page not found</h1>
        <p className="text-gray-500 text-sm mb-6">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="btn-primary no-underline">
          Go to Home
        </Link>
      </div>
    </PageContainer>
  );
}
