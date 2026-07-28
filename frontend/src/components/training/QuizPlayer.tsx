import React, { useState } from 'react';
import { submitQuizAttempt } from '@/services/trainingService';
import type { QuizAttemptRead, QuizRead } from '@/types/training.types';

interface QuizPlayerProps {
  courseId: string;
  quiz: QuizRead;
  onComplete: (result: QuizAttemptRead) => void;
}

export const QuizPlayer: React.FC<QuizPlayerProps> = ({ courseId, quiz, onComplete }) => {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleOptionSelect = (qId: string, opt: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: opt }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (Object.keys(answers).length < quiz.questions.length) {
      setError('Please answer all questions before submitting.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const payload = Object.entries(answers).map(([qId, opt]) => ({
        question_id: qId,
        selected_option: opt,
      }));

      const res = await submitQuizAttempt(courseId, payload);
      onComplete(res);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to submit quiz attempt.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-6">
      <div className="border-b pb-3 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{quiz.title}</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Passing Score: <strong className="text-emerald-700">{quiz.passing_score}%</strong> | Time Limit: {quiz.time_limit_minutes} mins
          </p>
        </div>
        <span className="px-3 py-1 bg-slate-100 text-slate-800 rounded font-mono text-xs font-bold border border-slate-300">
          {quiz.questions.length} Questions
        </span>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs font-semibold border border-red-200">
          ⚠️ {error}
        </div>
      )}

      <div className="space-y-6">
        {quiz.questions.map((q, idx) => (
          <div key={q.id} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
            <p className="text-xs font-bold text-gray-900">
              Q{idx + 1}. {q.question}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
              {[
                { label: 'A', text: q.option_a },
                { label: 'B', text: q.option_b },
                { label: 'C', text: q.option_c },
                { label: 'D', text: q.option_d },
              ].map((opt) => {
                const isSelected = answers[q.id] === opt.label;
                return (
                  <button
                    key={opt.label}
                    type="button"
                    onClick={() => handleOptionSelect(q.id, opt.label)}
                    className={`p-3 rounded-lg text-left border transition-all flex items-center gap-2 ${
                      isSelected
                        ? 'bg-slate-900 text-cyan-400 border-slate-900 font-bold shadow-md'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'
                    }`}
                  >
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${
                      isSelected ? 'bg-cyan-400 text-slate-900' : 'bg-slate-200 text-slate-700'
                    }`}>
                      {opt.label}
                    </span>
                    <span>{opt.text}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={submitting}
          className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg transition-colors shadow-md disabled:opacity-50"
        >
          {submitting ? 'Evaluating Quiz Answers...' : '✅ Submit Answers & Score Quiz'}
        </button>
      </div>
    </form>
  );
};
