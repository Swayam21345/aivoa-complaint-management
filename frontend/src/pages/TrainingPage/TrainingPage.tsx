import React, { useEffect, useState } from 'react';
import { TrainingCard } from '@/components/training/TrainingCard';
import { TrainingDashboard } from '@/components/training/TrainingDashboard';
import { createCourse, fetchCourseList, fetchTrainingDashboard } from '@/services/trainingService';
import type { TrainingCourseRead, TrainingDashboardRead } from '@/types/training.types';

export const TrainingPage: React.FC = () => {
  const [courses, setCourses] = useState<TrainingCourseRead[]>([]);
  const [dashboard, setDashboard] = useState<TrainingDashboardRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // New course form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('QUALITY');
  const [trainingType, setTrainingType] = useState('SOP');
  const [duration, setDuration] = useState(30);

  const loadData = async () => {
    setLoading(true);
    try {
      const [cRes, dRes] = await Promise.all([
        fetchCourseList({ search: search || undefined }),
        fetchTrainingDashboard(),
      ]);
      setCourses(cRes.items);
      setDashboard(dRes);
    } catch (err) {
      console.error('Failed to load training courses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search]);

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createCourse({
        title,
        description,
        category,
        training_type: trainingType,
        duration_minutes: duration,
        passing_score: 80.0,
        validity_days: 365,
      });
      setIsModalOpen(false);
      setTitle('');
      setDescription('');
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create course.');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b pb-4">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            🎓 GxP Training & Learning Management System
          </h1>
          <p className="text-xs text-gray-500 mt-1">21 CFR Part 11 & ISO 13485 Compliant Training Workflow</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800 transition-colors shadow-md"
        >
          ➕ Create Training Course
        </button>
      </div>

      {dashboard && <TrainingDashboard metrics={dashboard} />}

      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search courses by number, title, or description..."
          className="w-full md:w-96 rounded-lg border-gray-300 border p-2 text-xs"
        />
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-gray-500">Loading courses...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((c) => (
            <TrainingCard key={c.id} course={c} />
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleCreateCourse} className="bg-white rounded-xl p-6 max-w-md w-full space-y-4 shadow-2xl text-xs">
            <h3 className="font-bold text-gray-900 text-sm border-b pb-2">➕ Create New Training Course</h3>
            
            <div>
              <label className="block font-semibold mb-1">Course Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Good Manufacturing Practice (GMP) SOP"
                className="w-full rounded-lg border-gray-300 border p-2 text-xs"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1">Description</label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Course overview & learning objectives..."
                className="w-full rounded-lg border-gray-300 border p-2 text-xs"
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block font-semibold mb-1">Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full rounded-lg border-gray-300 border p-2 text-xs">
                  <option value="QUALITY">QUALITY</option>
                  <option value="SAFETY">SAFETY</option>
                  <option value="REGULATORY">REGULATORY</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">Type</label>
                <select value={trainingType} onChange={(e) => setTrainingType(e.target.value)} className="w-full rounded-lg border-gray-300 border p-2 text-xs">
                  <option value="SOP">SOP</option>
                  <option value="CAPA">CAPA</option>
                  <option value="RCA">RCA</option>
                  <option value="SAFETY">SAFETY</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold mb-1">Duration (min)</label>
                <input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full rounded-lg border-gray-300 border p-2 text-xs" />
              </div>
            </div>


            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-xs font-semibold">
                Cancel
              </button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold">
                Create Course
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default TrainingPage;
