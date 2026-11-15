import React from 'react';
import { AlertCircle, Inbox, RefreshCw } from 'lucide-react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="w-full space-y-3 p-6 animate-pulse">
      <div className="h-4 bg-slate-200 rounded w-1/4 mb-4" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 items-center">
          <div className="h-8 bg-slate-200 rounded w-1/6" />
          <div className="h-8 bg-slate-200 rounded w-2/6" />
          <div className="h-8 bg-slate-200 rounded w-1/6" />
          <div className="h-8 bg-slate-200 rounded w-2/6" />
        </div>
      ))}
    </div>
  );
};

export const EmptyState: React.FC<{
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}> = ({
  title = 'No records found',
  description = 'No transactional records match your active query filters.',
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-slate-200">
      <div className="p-3 bg-slate-100 rounded-full text-slate-400 mb-3">
        <Inbox className="w-8 h-8" />
      </div>
      <h3 className="text-sm font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-xs text-slate-500 max-w-sm mb-4">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-md text-xs font-medium transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};

export const ErrorAlert: React.FC<{
  title?: string;
  message?: string;
  onRetry?: () => void;
}> = ({
  title = 'Failed to load data',
  message = 'An unexpected error occurred while contacting the FastAPI backend.',
  onRetry,
}) => {
  return (
    <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 flex items-start gap-3">
      <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <h4 className="text-xs font-bold text-rose-900">{title}</h4>
        <p className="text-xs text-rose-700 mt-0.5">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-md transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Retry Connection</span>
          </button>
        )}
      </div>
    </div>
  );
};
