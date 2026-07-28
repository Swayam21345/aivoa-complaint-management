import { useState } from 'react';

import type { AIAnalysis, RiskLevel } from '@/types/complaint.types';
import { getRiskBadgeClass } from '@/utils/riskColors';

interface AICopilotPanelProps {
  aiAnalysis: AIAnalysis | null;
  loading?: boolean;
}

interface CollapsibleCardProps {
  title: string;
  icon: string;
  badge?: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

function CollapsibleCard({
  title,
  icon,
  badge,
  defaultOpen = true,
  children,
}: CollapsibleCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-gray-200 rounded-lg bg-white overflow-hidden transition-all shadow-xs">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full px-4 py-3 bg-gray-50/80 hover:bg-gray-100/80 flex items-center justify-between transition-colors text-left font-semibold text-xs text-gray-800"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm" role="img" aria-hidden="true">
            {icon}
          </span>
          <span>{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge}
          <span className="text-gray-400 text-xs font-mono">{isOpen ? '▲' : '▼'}</span>
        </div>
      </button>
      {isOpen && <div className="p-4 text-xs text-gray-700 space-y-3">{children}</div>}
    </div>
  );
}

export default function AICopilotPanel({ aiAnalysis, loading = false }: AICopilotPanelProps) {
  // ── Loading state ─────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="card p-6 border-l-4 border-primary-600 bg-gradient-to-br from-primary-50/40 to-white animate-pulse space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 rounded-full border-2 border-primary-600 border-t-transparent animate-spin" />
          <h3 className="text-xs font-bold text-primary-900 tracking-wide">
            AI Copilot is analyzing complaint...
          </h3>
        </div>
        <p className="text-xs text-gray-500">
          Running LangGraph workflow nodes: Ingest → Extract → Classify → Completeness → Root Cause → CAPA → Duplicate Detection.
        </p>
        <div className="space-y-2 pt-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-4 bg-gray-200 rounded w-1/2" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
        </div>
      </div>
    );
  }

  // ── Empty state ──────────────────────────────────────────────────────────────
  if (!aiAnalysis) {
    return (
      <div className="card p-5 border-l-4 border-gray-300 bg-gray-50/50">
        <div className="flex items-center gap-2 mb-2 text-gray-500 font-semibold text-sm">
          <span aria-hidden="true">✦</span>
          <span>Pharma QMS AI Copilot</span>
        </div>
        <p className="text-xs text-gray-500 leading-relaxed">
          No AI analysis generated yet. Upload a document or enter complaint details to trigger full AI QMS evaluation.
        </p>
      </div>
    );
  }

  const {
    summary,
    completeness,
    root_cause,
    capa,
    duplicates,
    risk_explanation,
    complaint_summary,
    root_cause_recommendation,
    capa_recommendation,
    risk_level,
    processing_time_ms,
    model_used,
  } = aiAnalysis;

  return (
    <div className="card p-5 border-l-4 border-primary-600 bg-gradient-to-br from-primary-50/20 to-white shadow-sm space-y-4">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-gray-100 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-primary-600 font-bold text-lg" aria-hidden="true">✦</span>
          <div>
            <h3 className="text-sm font-bold text-gray-900 tracking-tight">
              Pharma QMS AI Copilot
            </h3>
            <p className="text-[11px] text-gray-400">Intelligent Quality Surveillance & Investigation Assistant</p>
          </div>
        </div>

        {risk_level && (
          <span className={getRiskBadgeClass(risk_level)}>
            {risk_level} Risk
          </span>
        )}
      </div>

      {/* ── 1. Complaint Summary ──────────────────────────────────────────────── */}
      <CollapsibleCard title="Complaint Summary" icon="📝" defaultOpen={true}>
        <div className="space-y-2">
          <div>
            <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block mb-1">
              Short Summary
            </span>
            <p className="bg-gray-50 p-2.5 rounded border border-gray-200 text-gray-900 font-medium leading-relaxed">
              {summary?.short_summary || complaint_summary || 'Summary unavailable.'}
            </p>
          </div>

          {(summary?.detailed_summary || complaint_summary) && (
            <div>
              <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block mb-1">
                Detailed Analysis
              </span>
              <p className="bg-gray-50/70 p-2.5 rounded border border-gray-200 text-gray-700 leading-relaxed whitespace-pre-wrap">
                {summary?.detailed_summary || complaint_summary}
              </p>
            </div>
          )}
        </div>
      </CollapsibleCard>

      {/* ── 2. Completeness Score ────────────────────────────────────────────── */}
      <CollapsibleCard
        title="Intake Completeness Score"
        icon="📊"
        defaultOpen={true}
        badge={
          completeness ? (
            <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-100 text-indigo-800">
              {completeness.completeness_score}% Complete
            </span>
          ) : null
        }
      >
        {completeness ? (
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-[11px] font-semibold text-gray-600 mb-1">
                <span>Intake Quality Score</span>
                <span>{completeness.completeness_score}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all ${
                    completeness.completeness_score >= 80
                      ? 'bg-emerald-500'
                      : completeness.completeness_score >= 50
                        ? 'bg-amber-500'
                        : 'bg-red-500'
                  }`}
                  style={{ width: `${completeness.completeness_score}%` }}
                />
              </div>
            </div>

            {completeness.missing_fields.length > 0 && (
              <div>
                <span className="text-[11px] font-semibold text-amber-700 block mb-1">
                  Missing Key Fields
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {completeness.missing_fields.map((field) => (
                    <span
                      key={field}
                      className="px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200 rounded text-[11px] font-mono"
                    >
                      ! {field}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {completeness.recommendations.length > 0 && (
              <div>
                <span className="text-[11px] font-semibold text-gray-600 block mb-1">
                  Intake Recommendations
                </span>
                <ul className="list-disc list-inside space-y-1 text-gray-700">
                  {completeness.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 italic">Completeness check pending.</p>
        )}
      </CollapsibleCard>

      {/* ── 3. Root Cause Analysis ───────────────────────────────────────────── */}
      <CollapsibleCard
        title="Root Cause Hypothesis"
        icon="🔍"
        defaultOpen={true}
        badge={
          root_cause ? (
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-700">
              Conf: {Math.round(root_cause.confidence * 100)}%
            </span>
          ) : null
        }
      >
        {root_cause && root_cause.probable_root_causes.length > 0 ? (
          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-gray-600 block">
              Probable Root Causes:
            </span>
            <ul className="space-y-1.5">
              {root_cause.probable_root_causes.map((rc, idx) => (
                <li
                  key={idx}
                  className="bg-amber-50/50 p-2 rounded border border-amber-100 text-gray-800 flex items-start gap-2"
                >
                  <span className="text-amber-600 font-bold">•</span>
                  <span>{rc}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="bg-gray-50 p-3 rounded border border-gray-200 text-gray-800 leading-relaxed">
            {root_cause_recommendation || 'No root cause hypotheses identified.'}
          </p>
        )}
      </CollapsibleCard>

      {/* ── 4. CAPA Recommendations ───────────────────────────────────────────── */}
      <CollapsibleCard title="CAPA Recommendations" icon="🛡️" defaultOpen={true}>
        {capa ? (
          <div className="space-y-3">
            {capa.corrective_actions.length > 0 && (
              <div>
                <span className="text-[11px] font-bold text-red-700 uppercase tracking-wider block mb-1.5">
                  Corrective Actions (Immediate)
                </span>
                <ul className="space-y-1">
                  {capa.corrective_actions.map((act, i) => (
                    <li key={i} className="bg-red-50/40 p-2 rounded border border-red-100 text-red-900 font-medium">
                      ✓ {act}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {capa.preventive_actions.length > 0 && (
              <div>
                <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block mb-1.5">
                  Preventive Actions (Long-term)
                </span>
                <ul className="space-y-1">
                  {capa.preventive_actions.map((act, i) => (
                    <li key={i} className="bg-blue-50/40 p-2 rounded border border-blue-100 text-blue-900">
                      → {act}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-gray-50 p-3 rounded border border-gray-200 text-gray-800 leading-relaxed whitespace-pre-wrap">
            {capa_recommendation || 'No CAPA recommendations generated.'}
          </div>
        )}
      </CollapsibleCard>

      {/* ── 5. Duplicate Complaint Detection ──────────────────────────────────── */}
      <CollapsibleCard
        title="Duplicate Complaint Detection"
        icon="👯"
        defaultOpen={true}
        badge={
          duplicates ? (
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                duplicates.duplicate_found
                  ? 'bg-rose-100 text-rose-800 border border-rose-200'
                  : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {duplicates.duplicate_found ? 'Duplicate Flagged' : 'No Duplicates'}
            </span>
          ) : null
        }
      >
        {duplicates ? (
          <div className="space-y-2">
            {duplicates.duplicate_found ? (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded text-rose-900">
                <p className="font-semibold text-xs mb-1">
                  ⚠️ Potential Duplicate Complaints Found (Confidence: {Math.round(duplicates.confidence * 100)}%)
                </p>
                <div className="space-y-2 mt-2">
                  {duplicates.similar_complaints.map((sim, i) => (
                    <div key={i} className="bg-white p-2.5 rounded border border-rose-200 text-gray-800 flex items-center justify-between">
                      <div>
                        <span className="font-mono font-bold text-primary-600 mr-2">{sim.complaint_id}</span>
                        <span className="text-gray-600">{sim.summary}</span>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-rose-100 text-rose-800 rounded">
                        {Math.round(sim.similarity_score * 100)}% match
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-emerald-700 bg-emerald-50 p-2.5 rounded border border-emerald-200">
                ✓ No duplicate records detected in system (Confidence: {Math.round(duplicates.confidence * 100)}%).
              </p>
            )}
          </div>
        ) : (
          <p className="text-gray-500 italic">Duplicate scan pending.</p>
        )}
      </CollapsibleCard>

      {/* ── 6. Risk Explanation ──────────────────────────────────────────────── */}
      <CollapsibleCard
        title="Risk Classification Explanation"
        icon="⚠️"
        defaultOpen={true}
        badge={
          risk_explanation ? (
            <span className={getRiskBadgeClass(risk_explanation.risk_level as RiskLevel)}>
              {risk_explanation.risk_level} Risk
            </span>
          ) : null
        }
      >
        {risk_explanation ? (
          <div className="p-3 rounded border border-gray-200 bg-gray-50 space-y-1">
            <span className="text-[11px] font-bold text-gray-700 uppercase tracking-wider block">
              Risk Justification ({risk_explanation.risk_level}):
            </span>
            <p className="text-gray-800 leading-relaxed">
              {risk_explanation.explanation}
            </p>
          </div>
        ) : (
          <p className="text-gray-500 italic">Risk evaluation pending.</p>
        )}
      </CollapsibleCard>

      {/* Footer Meta */}
      {processing_time_ms != null && (
        <div className="pt-2 border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-400 font-mono">
          <span>LLM Engine: {model_used ?? 'gemma2-9b-it'}</span>
          <span>Latency: {(processing_time_ms / 1000).toFixed(2)}s</span>
        </div>
      )}
    </div>
  );
}
