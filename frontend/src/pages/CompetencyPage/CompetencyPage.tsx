import React, { useEffect, useState } from 'react';
import { CompetencyMatrix } from '@/components/training/CompetencyMatrix';
import { fetchCompetencyMatrix, verifyCompetency } from '@/services/trainingService';
import type { CompetencyRead } from '@/types/training.types';

export const CompetencyPage: React.FC = () => {
  const [matrix, setMatrix] = useState<CompetencyRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  const [userId, setUserId] = useState('');
  const [skill, setSkill] = useState('');
  const [level, setLevel] = useState('BEGINNER');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchCompetencyMatrix();
      setMatrix(data);
    } catch (err) {
      console.error('Failed to load competency matrix:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !skill) return;
    try {
      await verifyCompetency(userId, skill, level);
      setIsOpen(false);
      setSkill('');
      await loadData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to verify competency.');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 md:p-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-2xl font-black text-gray-900 flex items-center gap-2">
            🏅 GxP Employee Competency & Skill Tracking
          </h1>
          <p className="text-xs text-gray-500 mt-1">ISO 13485 Competency Verification & Qualification Records</p>
        </div>

        <button onClick={() => setIsOpen(true)} className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-bold hover:bg-slate-800">
          ➕ Verify Employee Competency
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-gray-500">Loading competency matrix...</div>
      ) : (
        <CompetencyMatrix records={matrix} />
      )}

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <form onSubmit={handleVerify} className="bg-white rounded-xl p-6 max-w-md w-full space-y-3 text-xs shadow-2xl">
            <h3 className="font-bold text-sm text-gray-900 border-b pb-2">➕ Verify Competency Record</h3>

            <div>
              <label className="block font-semibold mb-1">User ID *</label>
              <input type="text" required value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="UUID of Employee" className="w-full rounded border p-2 text-xs" />
            </div>

            <div>
              <label className="block font-semibold mb-1">Skill / Competency *</label>
              <input type="text" required value={skill} onChange={(e) => setSkill(e.target.value)} placeholder="e.g. Cleanroom Sterilization Protocol" className="w-full rounded border p-2 text-xs" />
            </div>

            <div>
              <label className="block font-semibold mb-1">Qualification Level</label>
              <select value={level} onChange={(e) => setLevel(e.target.value)} className="w-full rounded border p-2 text-xs">
                <option value="BEGINNER">BEGINNER</option>
                <option value="INTERMEDIATE">INTERMEDIATE</option>
                <option value="ADVANCED">ADVANCED</option>
                <option value="EXPERT">EXPERT</option>
              </select>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setIsOpen(false)} className="px-4 py-2 bg-gray-100 text-gray-700 font-semibold rounded">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-slate-900 text-white font-bold rounded">Verify Record</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default CompetencyPage;
