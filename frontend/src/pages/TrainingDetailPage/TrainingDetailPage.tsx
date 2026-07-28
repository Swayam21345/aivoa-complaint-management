import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { QuizPlayer } from '@/components/training/QuizPlayer';
import { addCourseQuiz, fetchCourseDetail, updateCourse } from '@/services/trainingService';
import type { QuizAttemptRead, TrainingCourseRead } from '@/types/training.types';

export const TrainingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [course, setCourse] = useState<TrainingCourseRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [quizResult, setQuizResult] = useState<QuizAttemptRead | null>(null);
  const [isAddQuizOpen, setIsAddQuizOpen] = useState(false);

  // New quiz questions state
  const [qText, setQText] = useState('');
  const [optA, setOptA] = useState('');
  const [optB, setOptB] = useState('');
  const [optC, setOptC] = useState('');
  const [optD, setOptD] = useState('');
  const [correctAns, setCorrectAns] = useState('A');

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await fetchCourseDetail(id);
      setCourse(data);
    } catch (err) {
      console.error('Failed to load course details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleActivate = async () => {
    if (!id) return;
    await updateCourse(id, { status: 'ACTIVE' });
    await loadData();
  };

  const handleAddQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    try {
      await addCourseQuiz(id, {
        title: `${course?.title} Comprehension Quiz`,
        passing_score: course?.passing_score || 80.0,
        randomize_questions: true,
        time_limit_minutes: 15,
        questions: [
          {
            question: qText,
            option_a: optA,
            option_b: optB,
            option_c: optC,
            option_d: optD,
            correct_answer: correctAns,
          },
        ],
      });
      setIsAddQuizOpen(false);
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to add quiz.');
    }
  };

  if (loading) return <div className="p-8 text-center text-xs text-gray-500">Loading course workspace...</div>;
  if (!course) return <div className="p-8 text-center text-xs text-red-500">Course not found.</div>;

  const quiz = course.quizzes?.[0];

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-4 md:p-6">
      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-xs text-primary-700 bg-primary-50 px-2 py-0.5 rounded border border-primary-200">
              {course.course_number}
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
              {course.status}
            </span>
          </div>
          <h1 className="text-xl font-bold text-gray-900 mt-2">{course.title}</h1>
          <p className="text-xs text-gray-500 mt-1">{course.description}</p>
        </div>

        {course.status === 'DRAFT' && (
          <button onClick={handleActivate} className="px-4 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg hover:bg-emerald-700">
            ⚡ Activate Course
          </button>
        )}
      </div>

      {quizResult ? (
        <div className={`p-6 rounded-xl border text-center space-y-3 ${quizResult.passed ? 'bg-emerald-50 border-emerald-300 text-emerald-900' : 'bg-red-50 border-red-300 text-red-900'}`}>
          <div className="text-4xl">{quizResult.passed ? '🎉' : '❌'}</div>
          <h3 className="text-lg font-bold">
            {quizResult.passed ? 'Congratulations! You Passed!' : 'Quiz Attempt Failed'}
          </h3>
          <p className="text-sm font-mono font-bold">
            Score: {quizResult.score}% (Passing Threshold: {course.passing_score}%)
          </p>
          <button onClick={() => setQuizResult(null)} className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold">
            Retake Quiz
          </button>
        </div>
      ) : quiz ? (
        <QuizPlayer courseId={course.id} quiz={quiz} onComplete={setQuizResult} />
      ) : (
        <div className="bg-white p-8 rounded-xl border border-gray-200 text-center space-y-3">
          <div className="text-3xl">📝</div>
          <h3 className="text-sm font-bold text-gray-700">No Active Quiz for this Course</h3>
          <button onClick={() => setIsAddQuizOpen(true)} className="px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg">
            ➕ Add Quiz Questions
          </button>
        </div>
      )}

      {/* Add Quiz Modal */}
      {isAddQuizOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleAddQuiz} className="bg-white rounded-xl p-6 max-w-lg w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">📝 Add Quiz Question</h3>

            <div>
              <label className="block font-semibold mb-1">Question Prompt</label>
              <textarea required value={qText} onChange={(e) => setQText(e.target.value)} rows={2} className="w-full rounded border p-2 text-xs" />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <input type="text" required placeholder="Option A" value={optA} onChange={(e) => setOptA(e.target.value)} className="rounded border p-2 text-xs" />
              <input type="text" required placeholder="Option B" value={optB} onChange={(e) => setOptB(e.target.value)} className="rounded border p-2 text-xs" />
              <input type="text" required placeholder="Option C" value={optC} onChange={(e) => setOptC(e.target.value)} className="rounded border p-2 text-xs" />
              <input type="text" required placeholder="Option D" value={optD} onChange={(e) => setOptD(e.target.value)} className="rounded border p-2 text-xs" />
            </div>

            <div>
              <label className="block font-semibold mb-1">Correct Answer</label>
              <select value={correctAns} onChange={(e) => setCorrectAns(e.target.value)} className="w-full rounded border p-2 text-xs">
                <option value="A">Option A</option>
                <option value="B">Option B</option>
                <option value="C">Option C</option>
                <option value="D">Option D</option>
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsAddQuizOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded font-semibold">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Save Quiz</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default TrainingDetailPage;
