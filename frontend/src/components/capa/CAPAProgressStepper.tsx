import type { CAPAStatus } from '@/types/capa.types';

interface Props {
  currentStatus: CAPAStatus | string;
}

const STEPS = [
  { id: 'OPEN', label: '1. Open' },
  { id: 'UNDER_IMPLEMENTATION', label: '2. Implementation' },
  { id: 'PENDING_EFFECTIVENESS', label: '3. Effectiveness Check' },
  { id: 'CLOSED', label: '4. Closed' },
];

export function CAPAProgressStepper({ currentStatus }: Props) {
  const getStepIndex = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 0;
      case 'UNDER_IMPLEMENTATION':
        return 1;
      case 'PENDING_EFFECTIVENESS':
      case 'EFFECTIVE':
      case 'INEFFECTIVE':
        return 2;
      case 'CLOSED':
        return 3;
      default:
        return 0;
    }
  };

  const currentIndex = getStepIndex(currentStatus);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6 shadow-xs">
      <div className="flex items-center justify-between relative">
        {/* Connecting Line */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 -translate-y-1/2 z-0" />
        <div
          className="absolute top-1/2 left-0 h-0.5 bg-blue-600 -translate-y-1/2 z-0 transition-all duration-300"
          style={{ width: `${(currentIndex / (STEPS.length - 1)) * 100}%` }}
        />

        {STEPS.map((step, index) => {
          const isDone = index < currentIndex || currentStatus === 'CLOSED';
          const isCurrent = index === currentIndex && currentStatus !== 'CLOSED';

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
                  isDone
                    ? 'bg-blue-600 text-white'
                    : isCurrent
                      ? 'bg-blue-600 text-white ring-4 ring-blue-100'
                      : 'bg-gray-100 text-gray-400 border border-gray-300'
                }`}
              >
                {isDone ? '✓' : index + 1}
              </div>
              <span
                className={`text-[11px] font-semibold mt-1.5 whitespace-nowrap ${
                  isCurrent ? 'text-blue-700' : isDone ? 'text-gray-900' : 'text-gray-400'
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
