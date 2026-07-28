import type { ReactNode } from 'react';

interface PageContainerProps {
  children: ReactNode;
  /** Optional page-level heading shown above children */
  title?: string;
  /** Optional subtitle shown below the title */
  subtitle?: string;
  /** Extra classes applied to the outer wrapper */
  className?: string;
}

/**
 * Consistent page wrapper: centres content, sets max-width, provides
 * standard vertical padding and optional page heading.
 */
export default function PageContainer({
  children,
  title,
  subtitle,
  className = '',
}: PageContainerProps) {
  return (
    <main className={`mx-auto max-w-screen-xl px-4 sm:px-6 lg:px-8 py-8 ${className}`}>
      {(title || subtitle) && (
        <div className="mb-6">
          {title && (
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
      )}
      {children}
    </main>
  );
}
