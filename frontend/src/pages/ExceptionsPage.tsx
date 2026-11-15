import React, { useEffect, useState } from 'react';
import { Search, Eye, X } from 'lucide-react';
import { ExceptionRecord, PaginatedResponse } from '../types';
import { getExceptions, ExceptionFilters } from '../services/api';
import { Pagination } from '../components/Pagination';
import { LoadingSkeleton, EmptyState, ErrorAlert } from '../components/StateFeedback';
import {
  formatINR,
  formatDate,
  formatAnomalyType,
  getSeverityStyle,
} from '../utils/formatters';

interface ExceptionsPageProps {
  onSelectException: (exceptionId: string) => void;
  initialSeverity?: string;
  initialAnomalyType?: string;
  refreshTrigger: number;
}

const ANOMALY_OPTIONS = [
  { value: 'ALL', label: 'All Anomaly Types' },
  { value: 'OVERBILLING_QUANTITY', label: 'Overbilling Quantity' },
  { value: 'OVERBILLING_AMOUNT', label: 'Overbilling Amount' },
  { value: 'UNDERBILLING', label: 'Underbilling' },
  { value: 'DUPLICATE_INVOICE', label: 'Duplicate Invoice' },
  { value: 'DUPLICATE_PAYMENT_ALLOCATION', label: 'Duplicate Payment Allocation' },
  { value: 'EXCESSIVE_PAYMENT_ALLOCATION', label: 'Excessive Payment Allocation' },
  { value: 'PREMATURE_ORDER_CLOSURE', label: 'Premature Order Closure' },
  { value: 'INVALID_STATUS_TRANSITION', label: 'Invalid Status Transition' },
  { value: 'DISPUTE_AR_DISCONNECT', label: 'Dispute AR Disconnect' },
  { value: 'SHORT_PAYMENT', label: 'Short Payment' },
  { value: 'SLA_AGING', label: 'SLA Aging' },
  { value: 'UNALLOCATED_CASH', label: 'Unallocated Cash' },
];

const SEVERITY_OPTIONS = [
  { value: 'ALL', label: 'All Severities' },
  { value: 'CRITICAL', label: 'CRITICAL' },
  { value: 'HIGH', label: 'HIGH' },
  { value: 'MEDIUM', label: 'MEDIUM' },
  { value: 'LOW', label: 'LOW' },
];

export const ExceptionsPage: React.FC<ExceptionsPageProps> = ({
  onSelectException,
  initialSeverity,
  initialAnomalyType,
  refreshTrigger,
}) => {
  const [data, setData] = useState<PaginatedResponse<ExceptionRecord> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters state
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState(initialSeverity || 'ALL');
  const [anomalyType, setAnomalyType] = useState(initialAnomalyType || 'ALL');

  // Update filters if props change
  useEffect(() => {
    if (initialSeverity) setSeverity(initialSeverity);
    if (initialAnomalyType) setAnomalyType(initialAnomalyType);
  }, [initialSeverity, initialAnomalyType]);

  const loadData = () => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const filters: ExceptionFilters = {
      page,
      limit,
      search: search.trim() || undefined,
      severity: severity !== 'ALL' ? severity : undefined,
      anomaly_type: anomalyType !== 'ALL' ? anomalyType : undefined,
    };

    getExceptions(filters)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to fetch exception records');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  };

  useEffect(() => {
    loadData();
  }, [page, severity, anomalyType, refreshTrigger]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  const handleResetFilters = () => {
    setSearch('');
    setSeverity('ALL');
    setAnomalyType('ALL');
    setPage(1);
  };

  const hasActiveFilters = search || severity !== 'ALL' || anomalyType !== 'ALL';

  return (
    <div className="p-8 space-y-6">
      {/* Search & Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search exceptions by ID (EXC-...), explanation, entity..."
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm"
          >
            Search
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Severity Filter */}
          <select
            value={severity}
            onChange={(e) => {
              setSeverity(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            {SEVERITY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Anomaly Type Filter */}
          <select
            value={anomalyType}
            onChange={(e) => {
              setAnomalyType(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 max-w-xs"
          >
            {ANOMALY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {hasActiveFilters && (
            <button
              onClick={handleResetFilters}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors text-xs flex items-center gap-1"
              title="Reset all filters"
            >
              <X className="w-4 h-4" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        {loading ? (
          <LoadingSkeleton rows={10} />
        ) : error ? (
          <div className="p-8">
            <ErrorAlert title="Failed to load exceptions" message={error} onRetry={loadData} />
          </div>
        ) : !data || data.items.length === 0 ? (
          <EmptyState
            title="No exceptions found"
            description="No compliance exceptions or leakage records match your filter criteria."
            actionText={hasActiveFilters ? 'Clear Filters' : undefined}
            onAction={hasActiveFilters ? handleResetFilters : undefined}
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold text-[11px]">
                  <tr>
                    <th className="px-6 py-3">Exception ID</th>
                    <th className="px-6 py-3">Anomaly Rule</th>
                    <th className="px-6 py-3">Target Entity</th>
                    <th className="px-6 py-3">Severity</th>
                    <th className="px-6 py-3 text-right">Leakage Amount</th>
                    <th className="px-6 py-3">Detected Date</th>
                    <th className="px-6 py-3 text-center">Evidence</th>
                    <th className="px-6 py-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.items.map((item) => {
                    const sevStyle = getSeverityStyle(item.severity);
                    return (
                      <tr
                        key={item.exception_id}
                        className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                        onClick={() => onSelectException(item.exception_id)}
                      >
                        <td className="px-6 py-3.5 font-mono font-medium text-slate-900">
                          {item.business_id}
                        </td>
                        <td className="px-6 py-3.5">
                          <span className="font-semibold text-slate-800 block">
                            {formatAnomalyType(item.issue_type)}
                          </span>
                          <span className="text-[11px] text-slate-400 line-clamp-1 max-w-xs">
                            {item.explanation}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-slate-600">
                          <span className="font-semibold text-slate-700">{item.entity_type}</span>{' '}
                          <span className="font-mono text-slate-400">({item.entity_id.slice(0, 8)}...)</span>
                        </td>
                        <td className="px-6 py-3.5">
                          <span
                            className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${sevStyle.bg} ${sevStyle.text} ${sevStyle.border}`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${sevStyle.dot}`} />
                            {item.severity}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono font-bold text-slate-900">
                          {item.leakage_amount !== null && item.leakage_amount !== undefined
                            ? formatINR(item.leakage_amount)
                            : '-'}
                        </td>
                        <td className="px-6 py-3.5 text-slate-500 whitespace-nowrap">
                          {formatDate(item.detected_at)}
                        </td>
                        <td className="px-6 py-3.5 text-center">
                          <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[11px] font-semibold">
                            {item.evidence_count} items
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => onSelectException(item.exception_id)}
                            className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded font-semibold text-[11px] transition-colors"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>View Dossier</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <Pagination
              page={data.page}
              pages={data.pages}
              total={data.total}
              limit={data.limit}
              onPageChange={(newPage) => setPage(newPage)}
              disabled={loading}
            />
          </>
        )}
      </div>
    </div>
  );
};
