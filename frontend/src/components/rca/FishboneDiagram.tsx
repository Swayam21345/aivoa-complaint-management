import React from 'react';
import type { FishboneCategories } from '@/types/rca.types';

interface FishboneDiagramProps {
  categories?: FishboneCategories;
  primaryCause?: string;
}

export const FishboneDiagram: React.FC<FishboneDiagramProps> = ({ categories, primaryCause }) => {
  const cats = [
    { title: '👨‍🔧 Manpower', items: categories?.manpower || [] },
    { title: '⚙️ Machine', items: categories?.machine || [] },
    { title: '📦 Material', items: categories?.material || [] },
    { title: '📋 Method', items: categories?.method || [] },
    { title: '📏 Measurement', items: categories?.measurement || [] },
    { title: '🌱 Milieu / Env', items: categories?.milieu || [] },
  ];

  return (
    <div className="bg-slate-900 text-slate-100 p-6 rounded-xl border border-slate-800 shadow-xl overflow-x-auto">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h4 className="text-sm font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
          🐟 6M Ishikawa (Fishbone) Diagram
        </h4>
        <span className="text-xs text-slate-400">Multi-Factorial Cause Analysis</span>
      </div>

      <div className="relative min-w-[700px] py-6">
        {/* Spine */}
        <div className="absolute top-1/2 left-0 right-36 h-1 bg-cyan-500 rounded-full shadow-cyan-500/50 shadow-md"></div>

        {/* Head */}
        <div className="absolute top-1/2 right-0 -translate-y-1/2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-4 py-3 rounded-lg border border-cyan-400 shadow-lg max-w-[200px] text-center">
          <p className="text-[10px] uppercase font-bold tracking-wider text-cyan-200">Problem / Defect</p>
          <p className="text-xs font-semibold leading-tight line-clamp-2 mt-1">
            {primaryCause || 'Root Cause Identified'}
          </p>
        </div>

        {/* 6M Category Bones Grid */}
        <div className="grid grid-cols-3 gap-6 relative z-10 pr-40">
          {cats.map((cat, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border ${
                idx < 3 ? 'bg-slate-800/80 border-slate-700' : 'bg-slate-800/60 border-slate-700/80'
              }`}
            >
              <h5 className="text-xs font-bold text-cyan-300 mb-2 border-b border-slate-700 pb-1">
                {cat.title}
              </h5>
              {cat.items.length > 0 ? (
                <ul className="space-y-1">
                  {cat.items.map((item, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-1.5">
                      <span className="text-cyan-500 text-[10px]">▶</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[11px] italic text-slate-500">No factors noted</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
