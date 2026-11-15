import React from 'react';
import { formatAnomalyType } from '../utils/formatters';

interface AnomalyTypeBreakdownProps {
  anomalyCounts: Record<string, number>;
  totalExceptions: number;
  onSelectAnomaly?: (anomalyType: string) => void;
}

export const AnomalyTypeBreakdown: React.FC<AnomalyTypeBreakdownProps> = ({
  anomalyCounts,
  totalExceptions,
  onSelectAnomaly,
}) => {
  // Sort descending by count
  const sortedEntries = Object.entries(anomalyCounts).sort((a, b) => b[1] - a[1]);
  const maxCount = Math.max(...Object.values(anomalyCounts), 1);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900">Anomaly Rule Breakdown</h2>
          <p className="text-xs text-slate-500 mt-0.5">Identified leakage and process violations by detector</p>
        </div>
        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
          {sortedEntries.length} Active Categories
        </span>
      </div>

      {sortedEntries.length === 0 ? (
        <p className="text-xs text-slate-400 py-4 text-center">No anomalies recorded.</p>
      ) : (
        <div className="space-y-3">
          {sortedEntries.map(([issueType, count]) => {
            const barWidth = Math.min(100, Math.max(8, (count / maxCount) * 100));
            const percentage = totalExceptions > 0 ? ((count / totalExceptions) * 100).toFixed(1) : '0';

            return (
              <div
                key={issueType}
                onClick={() => onSelectAnomaly && onSelectAnomaly(issueType)}
                className={`p-2.5 rounded-lg border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all ${
                  onSelectAnomaly ? 'cursor-pointer' : ''
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="font-semibold text-slate-800">
                    {formatAnomalyType(issueType)}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-900">{count}</span>
                    <span className="text-[11px] text-slate-400">({percentage}%)</span>
                  </div>
                </div>

                <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${barWidth}%` }}
                    className="h-full bg-blue-600 rounded-full transition-all duration-300"
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
