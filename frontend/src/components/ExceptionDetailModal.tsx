import React, { useEffect, useState } from 'react';
import {
  X,
  AlertTriangle,
  FileText,
  DollarSign,
  Database,
  Code2,
} from 'lucide-react';
import { ExceptionDetail } from '../types';
import { getExceptionDetail } from '../services/api';
import {
  formatINR,
  formatDate,
  formatAnomalyType,
  getSeverityStyle,
} from '../utils/formatters';

interface ExceptionDetailModalProps {
  exceptionId: string | null;
  onClose: () => void;
}

export const ExceptionDetailModal: React.FC<ExceptionDetailModalProps> = ({
  exceptionId,
  onClose,
}) => {
  const [detail, setDetail] = useState<ExceptionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!exceptionId) {
      setDetail(null);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    getExceptionDetail(exceptionId)
      .then((data) => {
        if (isMounted) {
          setDetail(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to fetch exception dossier');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [exceptionId]);

  if (!exceptionId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-rose-100 rounded-lg text-rose-700">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">
                  {detail ? detail.business_id : 'Exception Dossier'}
                </h3>
                {detail && (
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                      getSeverityStyle(detail.severity).bg
                    } ${getSeverityStyle(detail.severity).text} ${
                      getSeverityStyle(detail.severity).border
                    }`}
                  >
                    {detail.severity}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                UUID: {exceptionId}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-16 text-center">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-xs text-slate-500">Loading exception dossier &amp; evidence...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
              <p className="font-bold">Error loading dossier</p>
              <p>{error}</p>
            </div>
          ) : detail ? (
            <>
              {/* Top KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-4">
                  <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider block mb-1">
                    Financial Leakage (INR)
                  </span>
                  <span className="text-xl font-bold text-rose-900">
                    {detail.leakage_amount !== null && detail.leakage_amount !== undefined
                      ? formatINR(detail.leakage_amount)
                      : 'None Identified'}
                  </span>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    Anomaly Classification
                  </span>
                  <span className="text-sm font-bold text-slate-900">
                    {formatAnomalyType(detail.issue_type)}
                  </span>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
                    Target Entity
                  </span>
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                    <span className="px-1.5 py-0.5 bg-slate-200 rounded text-[10px]">
                      {detail.entity_type}
                    </span>
                    <span className="font-mono">{detail.entity_id.slice(0, 8)}...</span>
                  </div>
                </div>
              </div>

              {/* Root Cause & Explanation */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-600" />
                  Violation Explanation &amp; Root Cause
                </h4>
                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-100">
                  {detail.explanation}
                </p>

                <div className="mt-3 pt-3 border-t border-slate-100">
                  <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-1.5">
                    Recommended Remediation
                  </span>
                  <div className="text-xs text-emerald-800 bg-emerald-50/70 border border-emerald-200 rounded-lg p-3 font-medium">
                    {detail.recommended_action}
                  </div>
                </div>
              </div>

              {/* Expected vs Actual Values Comparison */}
              {detail.evidence_items && detail.evidence_items.length > 0 && (
                <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-amber-600" />
                    Expected vs. Actual Discrepancy Analysis
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    {detail.evidence_items.map((ev, idx) => (
                      <React.Fragment key={ev.evidence_id || idx}>
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                            Expected Benchmark
                          </span>
                          <span className="text-sm font-mono font-bold text-slate-800">
                            {ev.expected_value !== null && ev.expected_value !== undefined
                              ? formatINR(ev.expected_value)
                              : 'Standard Process SLA'}
                          </span>
                        </div>

                        <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg">
                          <span className="text-[10px] uppercase font-bold text-amber-600 block mb-1">
                            Actual Recorded Value
                          </span>
                          <span className="text-sm font-mono font-bold text-amber-900">
                            {ev.actual_value !== null && ev.actual_value !== undefined
                              ? formatINR(ev.actual_value)
                              : 'Discrepancy Detected'}
                          </span>
                        </div>

                        <div className="p-3 bg-rose-50/70 border border-rose-200 rounded-lg">
                          <span className="text-[10px] uppercase font-bold text-rose-600 block mb-1">
                            Discrepancy Delta
                          </span>
                          <span className="text-sm font-mono font-bold text-rose-700">
                            {ev.discrepancy_delta !== null && ev.discrepancy_delta !== undefined
                              ? formatINR(ev.discrepancy_delta)
                              : 'Process Divergence'}
                          </span>
                        </div>
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}

              {/* Substantiating Evidence Payloads */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <Database className="w-4 h-4 text-indigo-600" />
                    Substantiating Evidence ({detail.evidence_items.length} Records)
                  </h4>
                  <span className="text-[11px] text-slate-500">
                    Source audit trail from PostgreSQL
                  </span>
                </div>

                {detail.evidence_items.length === 0 ? (
                  <p className="text-xs text-slate-400 py-3">No separate evidence payloads attached.</p>
                ) : (
                  <div className="space-y-3">
                    {detail.evidence_items.map((ev, index) => (
                      <div
                        key={ev.evidence_id || index}
                        className="border border-slate-200 rounded-lg p-3 bg-slate-50/50 space-y-2 text-xs"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-2">
                          <span className="font-semibold text-slate-800">
                            Evidence Item #{index + 1}: {ev.evidence_type}
                          </span>
                          <span className="font-mono text-[10px] text-slate-400">
                            Table: <strong className="text-slate-700">{ev.source_table}</strong> | ID: {ev.source_id.slice(0, 8)}...
                          </span>
                        </div>

                        {ev.conflicting_source_table && (
                          <div className="text-[11px] text-rose-700 bg-rose-50 px-2 py-1 rounded border border-rose-100 flex items-center gap-2">
                            <span>Conflicting Reference:</span>
                            <span className="font-mono font-bold">
                              {ev.conflicting_source_table} ({ev.conflicting_source_id?.slice(0, 8)}...)
                            </span>
                          </div>
                        )}

                        <div>
                          <span className="text-[10px] font-bold uppercase text-slate-400 flex items-center gap-1 mb-1">
                            <Code2 className="w-3 h-3" /> Audit Payload JSON
                          </span>
                          <pre className="text-[11px] font-mono bg-slate-900 text-slate-100 p-3 rounded-lg overflow-x-auto max-h-48 leading-tight">
                            {JSON.stringify(ev.evidence_payload, null, 2)}
                          </pre>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500">
            Audit Record: Detected at {detail ? formatDate(detail.detected_at) : '-'}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-medium transition-colors"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};
