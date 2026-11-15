import React, { useEffect, useState } from 'react';
import {
  Users,
  ShoppingCart,
  FileText,
  CreditCard,
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { DashboardSummary, ExceptionRecord, NavigationTab } from '../types';
import { getDashboardSummary, getExceptions } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { SeverityDistribution } from '../components/SeverityDistribution';
import { AnomalyTypeBreakdown } from '../components/AnomalyTypeBreakdown';
import { LoadingSkeleton, ErrorAlert } from '../components/StateFeedback';
import {
  formatINR,
  formatCompactINR,
  formatDate,
  formatAnomalyType,
  getSeverityStyle,
} from '../utils/formatters';

interface OverviewPageProps {
  onNavigateTab: (tab: NavigationTab, filter?: { severity?: string; anomaly_type?: string }) => void;
  onSelectException: (exceptionId: string) => void;
  refreshTrigger: number;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  onNavigateTab,
  onSelectException,
  refreshTrigger,
}) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentExceptions, setRecentExceptions] = useState<ExceptionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    Promise.all([
      getDashboardSummary(),
      getExceptions({ page: 1, limit: 6 }),
    ])
      .then(([summaryData, exceptionsData]) => {
        if (isMounted) {
          setSummary(summaryData);
          setRecentExceptions(exceptionsData.items);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || 'Failed to load executive summary');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [refreshTrigger]);

  if (loading) {
    return <LoadingSkeleton rows={8} />;
  }

  if (error || !summary) {
    return (
      <div className="p-8">
        <ErrorAlert
          title="Could not load Executive Dashboard"
          message={error || 'Unable to connect to FastAPI backend summary endpoint.'}
          onRetry={() => {
            setLoading(true);
            setError(null);
          }}
        />
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      {/* Top Operational & Financial KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          title="Total Accounts"
          value={summary.total_accounts.toLocaleString('en-IN')}
          subtitle="Customer Master Records"
          icon={Users}
          variant="default"
        />

        <KpiCard
          title="Total Orders"
          value={summary.total_sales_orders.toLocaleString('en-IN')}
          subtitle="Commercial Sales Orders"
          icon={ShoppingCart}
          variant="info"
        />

        <KpiCard
          title="Total Invoices"
          value={summary.total_invoices.toLocaleString('en-IN')}
          subtitle="AR Billing Documents"
          icon={FileText}
          variant="default"
        />

        <KpiCard
          title="Total Payments"
          value={summary.total_payments.toLocaleString('en-IN')}
          subtitle="Settlements & Remittances"
          icon={CreditCard}
          variant="success"
        />

        <KpiCard
          title="Total Exceptions"
          value={summary.total_detected_exceptions.toLocaleString('en-IN')}
          subtitle="Policy & Integrity Breaches"
          icon={AlertTriangle}
          variant="warning"
          badge="12 Detectors"
        />

        <KpiCard
          title="Revenue Leakage"
          value={formatCompactINR(summary.total_identified_leakage_amount)}
          subtitle={formatINR(summary.total_identified_leakage_amount)}
          icon={ShieldAlert}
          variant="danger"
        />
      </div>

      {/* Visual Analytics Grid: Severity & Anomaly Type Breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SeverityDistribution
          severityCounts={summary.exception_counts_by_severity}
          totalExceptions={summary.total_detected_exceptions}
          onSelectSeverity={(severity) => onNavigateTab('exceptions', { severity })}
        />

        <AnomalyTypeBreakdown
          anomalyCounts={summary.exception_counts_by_anomaly_type}
          totalExceptions={summary.total_detected_exceptions}
          onSelectAnomaly={(anomaly_type) => onNavigateTab('exceptions', { anomaly_type })}
        />
      </div>

      {/* Recent Exceptions Preview Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Recent Detected Exceptions</h2>
            <p className="text-xs text-slate-500 mt-0.5">Latest high-risk leakage items flagged by the detection engine</p>
          </div>
          <button
            onClick={() => onNavigateTab('exceptions')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
          >
            <span>View All Exceptions</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentExceptions.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No exceptions currently logged in the system.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold text-[11px]">
                <tr>
                  <th className="px-6 py-3">Exception ID</th>
                  <th className="px-6 py-3">Anomaly Rule</th>
                  <th className="px-6 py-3">Entity Reference</th>
                  <th className="px-6 py-3">Severity</th>
                  <th className="px-6 py-3 text-right">Identified Leakage</th>
                  <th className="px-6 py-3">Detected At</th>
                  <th className="px-6 py-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentExceptions.map((item) => {
                  const sevStyle = getSeverityStyle(item.severity);
                  return (
                    <tr key={item.exception_id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-6 py-3.5 font-mono font-medium text-slate-900">
                        {item.business_id}
                      </td>
                      <td className="px-6 py-3.5 font-medium text-slate-800">
                        {formatAnomalyType(item.issue_type)}
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
                      <td className="px-6 py-3.5 text-slate-500">
                        {formatDate(item.detected_at)}
                      </td>
                      <td className="px-6 py-3.5 text-center">
                        <button
                          onClick={() => onSelectException(item.exception_id)}
                          className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-medium text-[11px] transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
