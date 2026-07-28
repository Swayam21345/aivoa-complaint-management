import React from 'react';
import type { FiveWhyItem } from '@/types/rca.types';

interface FiveWhysFormProps {
  items?: FiveWhyItem[];
}

export const FiveWhysForm: React.FC<FiveWhysFormProps> = ({ items }) => {
  if (!items || items.length === 0) {
    return <div className="text-xs text-gray-500 italic p-4">No 5 Whys items recorded.</div>;
  }

  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div
          key={item.step}
          className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:border-primary-300 transition-colors"
        >
          <div className="flex-shrink-0 w-7 h-7 rounded-full bg-primary-100 text-primary-700 font-bold text-xs flex items-center justify-center border border-primary-200">
            W{item.step}
          </div>
          <div className="flex-1 text-xs">
            <p className="font-semibold text-gray-800">
              <span className="text-gray-500 mr-1">Why #{item.step}:</span> {item.question}
            </p>
            <p className="text-gray-600 mt-1 bg-gray-50 p-2 rounded border border-gray-100">
              <span className="font-semibold text-primary-600 mr-1">Answer:</span> {item.answer}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};
