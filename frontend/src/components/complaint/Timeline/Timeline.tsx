import { StatusBadge } from '@/components/common/Badge/Badges';
import { formatDateTime } from '@/utils/formatDate';

export interface TimelineEventItem {
  id: string;
  event_type: string;
  title: string;
  description?: string | null;
  author?: string | null;
  timestamp: string;
  icon: string;
  status?: string | null;
}

interface TimelineProps {
  events: TimelineEventItem[];
  loading?: boolean;
}

export default function Timeline({ events, loading = false }: TimelineProps) {
  if (loading) {
    return (
      <div className="space-y-4 p-4 animate-pulse">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-gray-200" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center text-xs text-gray-400 italic">
        No audit events recorded for this complaint timeline.
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-200">
      {events.map((event) => (
        <div key={event.id} className="relative flex items-start gap-4 group">
          {/* Node Icon */}
          <div className="absolute -left-6 top-0 w-6 h-6 rounded-full bg-white border-2 border-primary-600 flex items-center justify-center text-xs shadow-xs z-10">
            <span>{event.icon || '📌'}</span>
          </div>

          {/* Event Content Card */}
          <div className="flex-1 bg-white p-3.5 rounded-lg border border-gray-200 shadow-2xs hover:border-primary-300 transition-colors">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-gray-900">{event.title}</span>
                {event.status && <StatusBadge status={event.status} />}
              </div>
              <span className="text-[11px] text-gray-400 font-mono">
                {formatDateTime(event.timestamp)}
              </span>
            </div>

            {event.description && (
              <p className="text-xs text-gray-700 leading-relaxed mt-1 whitespace-pre-wrap">
                {event.description}
              </p>
            )}

            {event.author && (
              <div className="mt-2 pt-1.5 border-t border-gray-100 flex items-center justify-between text-[10px] text-gray-400">
                <span>By: {event.author}</span>
                <span className="font-mono uppercase">{event.event_type}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
