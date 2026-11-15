import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, RefreshCw, Database, Server } from 'lucide-react';

export type ComponentStatus = 'connected' | 'disconnected' | 'loading' | 'degraded';

interface StatusCardProps {
  title: string;
  iconType: 'server' | 'database';
  status: ComponentStatus;
  statusText: string;
  endpoint: string;
  details?: Record<string, any>;
  errorMessage?: string;
  lastChecked?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({
  title,
  iconType,
  status,
  statusText,
  endpoint,
  details,
  errorMessage,
  lastChecked,
}) => {
  const Icon = iconType === 'server' ? Server : Database;

  const getStatusBadge = () => {
    switch (status) {
      case 'connected':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            OPERATIONAL
          </span>
        );
      case 'disconnected':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300">
            <XCircle className="w-3.5 h-3.5 text-rose-600" />
            DISCONNECTED
          </span>
        );
      case 'loading':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300">
            <RefreshCw className="w-3.5 h-3.5 text-amber-600 animate-spin" />
            CHECKING...
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-800 border border-slate-300">
            <AlertTriangle className="w-3.5 h-3.5 text-slate-600" />
            UNKNOWN
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-100 text-slate-700">
            <Icon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-lg">{title}</h3>
            <p className="text-xs text-slate-500 font-mono">{endpoint}</p>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      <div className="space-y-2 text-sm pt-3 border-t border-slate-100">
        <div className="flex justify-between text-slate-600">
          <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">Status</span>
          <span className="font-medium text-slate-900">{statusText}</span>
        </div>

        {details && Object.entries(details).map(([key, value]) => (
          <div key={key} className="flex justify-between text-slate-600">
            <span className="text-xs uppercase tracking-wider text-slate-400 font-medium">{key}</span>
            <span className="font-mono text-xs text-slate-800">{String(value)}</span>
          </div>
        ))}

        {errorMessage && (
          <div className="mt-3 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700">
            <div className="font-semibold mb-1 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" /> Error Details
            </div>
            <p className="font-mono break-all">{errorMessage}</p>
          </div>
        )}

        {lastChecked && (
          <div className="pt-2 text-right text-[11px] text-slate-400">
            Last checked: {lastChecked}
          </div>
        )}
      </div>
    </div>
  );
};
