import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { DisputeItem, PaginatedResponse } from '../types';
import { getDisputes, TransactionFilters } from '../services/api';
import { Pagination } from '../components/Pagination';
import { LoadingSkeleton, EmptyState, ErrorAlert } from '../components/StateFeedback';
import { formatINR, formatDate, getStatusStyle } from '../utils/formatters';

interface DisputesPageProps {
  refreshTrigger: number;
}

const STATUS_OPTIONS = [
  { value: 'ALL', label: 'All Statuses' },
  { value: 'OPEN', label: 'OPEN' },
  { value: 'UNDER_REVIEW', label: 'UNDER_REVIEW' },
  { value: 'RESOLVED', label: 'RESOLVED' },
  { value: 'REJECTED', label: 'REJECTED' },
];

export const DisputesPage: React.FC<DisputesPageProps> = ({ refreshTrigger }) => {
  const [data, setData] = useState<PaginatedResponse<DisputeItem> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('ALL');

  const loadData = () => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const filters: TransactionFilters = {
      page,
      limit,
      search: search.trim() || undefined,
      status: status !== 'ALL' ? status : undefined,
    };

    getDisputes(filters)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to fetch disputes');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  };

  useEffect(() => {
    loadData();
  }, [page, status, refreshTrigger]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

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
              placeholder="Search by Dispute ID (DISP-...)"
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-3">
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="px-3 py-2 border border-slate-200 rounded-lg text-xs bg-white text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Table Card */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        {loading ? (
          <LoadingSkeleton rows={10} />
        ) : error ? (
          <div className="p-8">
            <ErrorAlert title="Failed to load disputes" message={error} onRetry={loadData} />
          </div>
        ) : !data || data.items.length === 0 ? (
          <EmptyState
            title="No disputes found"
            description="No customer billing disputes match your query."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold text-[11px]">
                  <tr>
                    <th className="px-6 py-3">Dispute ID</th>
                    <th className="px-6 py-3">Invoice Reference</th>
                    <th className="px-6 py-3">Dispute Reason</th>
                    <th className="px-6 py-3 text-right">Disputed Amount</th>
                    <th className="px-6 py-3">Lodged Date</th>
                    <th className="px-6 py-3">Resolved Date</th>
                    <th className="px-6 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.items.map((disp) => {
                    const stStyle = getStatusStyle(disp.status);
                    return (
                      <tr key={disp.dispute_id} className="hover:bg-slate-50/70 transition-colors">
                        <td className="px-6 py-3.5 font-mono font-semibold text-slate-900">
                          {disp.business_id}
                        </td>
                        <td className="px-6 py-3.5 font-mono text-slate-600">
                          {disp.invoice_id.slice(0, 8)}...
                        </td>
                        <td className="px-6 py-3.5 text-slate-700 font-medium">
                          {disp.dispute_reason}
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono font-bold text-rose-700">
                          {formatINR(disp.disputed_amount)}
                        </td>
                        <td className="px-6 py-3.5 text-slate-600">
                          {formatDate(disp.lodged_at)}
                        </td>
                        <td className="px-6 py-3.5 text-slate-500">
                          {disp.resolved_at ? formatDate(disp.resolved_at) : '-'}
                        </td>
                        <td className="px-6 py-3.5">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${stStyle.bg} ${stStyle.text} ${stStyle.border}`}
                          >
                            {disp.status}
                          </span>
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
