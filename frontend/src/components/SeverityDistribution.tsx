import React from 'react';
import { getSeverityStyle } from '../utils/formatters';

interface SeverityDistributionProps {
  severityCounts: Record<string, number>;
  totalExceptions: number;
  onSelectSeverity?: (severity: string) => void;
}

const SEVERITY_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

export const SeverityDistribution: React.FC<SeverityDistributionProps> = ({
  severityCounts,
  totalExceptions,
  onSelectSeverity,
}) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Exception Severity Distribution</h2>
          <p className="text-xs text-slate-500 mt-0.5">Classification by operational and financial risk</p>
        </div>
        <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md">
          {totalExceptions} Total
        </span>
      </div>

      {/* Stacked Progress Bar */}
      {totalExceptions > 0 ? (
        <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex mb-5 shadow-inner">
          {SEVERITY_ORDER.map((sev) => {
            const count = severityCounts[sev] || 0;
            if (count === 0) return null;
            const pct = (count / totalExceptions) * 100;
            const bgClass =
              sev === 'CRITICAL'
                ? 'bg-rose-500'
                : sev === 'HIGH'
                ? 'bg-orange-500'
                : sev === 'MEDIUM'
                ? 'bg-amber-400'
                : 'bg-blue-500';
            return (
              <div
                key={sev}
                style={{ width: `${pct}%` }}
                className={`${bgClass} transition-all duration-300 relative group`}
                title={`${sev}: ${count} (${pct.toFixed(1)}%)`}
              />
            );
          })}
        </div>
      ) : (
        <div className="w-full h-3 bg-slate-100 rounded-full mb-5" />
      )}

      {/* Severity Grid Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {SEVERITY_ORDER.map((sev) => {
          const count = severityCounts[sev] || 0;
          const pct = totalExceptions > 0 ? ((count / totalExceptions) * 100).toFixed(1) : '0';
          const style = getSeverityStyle(sev);

          return (
            <div
              key={sev}
              onClick={() => onSelectSeverity && onSelectSeverity(sev)}
              className={`p-3.5 rounded-lg border ${style.border} ${style.bg} transition-all ${
                onSelectSeverity ? 'cursor-pointer hover:shadow-sm hover:scale-[1.02]' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-[11px] font-bold ${style.text}`}>{sev}</span>
                <span className={`w-2 h-2 rounded-full ${style.dot}`} />
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-lg font-bold text-slate-900">{count}</span>
                <span className="text-[11px] text-slate-500 font-medium">({pct}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
