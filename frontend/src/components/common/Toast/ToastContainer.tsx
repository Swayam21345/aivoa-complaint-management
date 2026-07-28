import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { removeToast, type ToastMessage } from '@/store/slices/toastSlice';

function ToastItem({ toast }: { toast: ToastMessage }) {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(removeToast(toast.id));
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast.id, dispatch]);

  const styleMap = {
    success: 'bg-emerald-800 text-white border-emerald-900',
    error: 'bg-red-800 text-white border-red-900',
    warning: 'bg-amber-800 text-white border-amber-900',
    info: 'bg-primary-800 text-white border-primary-900',
  };

  const iconMap = {
    success: '✅',
    error: '🚨',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div
      className={`flex items-start gap-3 p-3.5 rounded-lg shadow-lg border text-xs max-w-sm w-full transition-all animate-bounce-short ${
        styleMap[toast.type]
      }`}
      role="alert"
    >
      <span className="text-base leading-none">{iconMap[toast.type]}</span>
      <div className="flex-1">
        <h4 className="font-bold">{toast.title}</h4>
        {toast.message && <p className="mt-0.5 opacity-90 leading-tight">{toast.message}</p>}
      </div>
      <button
        type="button"
        onClick={() => dispatch(removeToast(toast.id))}
        className="opacity-70 hover:opacity-100 text-sm font-bold leading-none px-1"
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const toasts = useAppSelector((state) => state.toast.toasts);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-auto">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}
