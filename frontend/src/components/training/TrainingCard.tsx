import React from 'react';
import { Link } from 'react-router-dom';
import type { TrainingCourseRead } from '@/types/training.types';

interface TrainingCardProps {
  course: TrainingCourseRead;
}

export const TrainingCard: React.FC<TrainingCardProps> = ({ course }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow space-y-3 flex flex-col justify-between">
      <div>
        <div className="flex justify-between items-start gap-2 mb-2">
          <span className="font-mono font-bold text-xs text-primary-700 bg-primary-50 px-2 py-0.5 rounded border border-primary-200">
            {course.course_number}
          </span>
          <span
            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
              course.status === 'ACTIVE'
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                : 'bg-amber-100 text-amber-800 border border-amber-200'
            }`}
          >
            {course.status}
          </span>
        </div>

        <h3 className="font-bold text-gray-900 text-sm line-clamp-2">{course.title}</h3>
        <p className="text-xs text-gray-500 line-clamp-2 mt-1">{course.description || 'No description provided.'}</p>
      </div>

      <div className="pt-3 border-t border-gray-100 flex items-center justify-between text-xs">
        <div className="text-gray-500 space-y-0.5">
          <p>⏱️ {course.duration_minutes} mins | 🎯 {course.passing_score}% Pass</p>
          <p className="text-[10px] text-gray-400">Category: {course.category}</p>
        </div>

        <Link
          to={`/training/${course.id}`}
          className="px-3 py-1.5 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800 transition-colors text-xs"
        >
          View Course →
        </Link>
      </div>
    </div>
  );
};
