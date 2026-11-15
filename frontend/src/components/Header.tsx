import React from 'react';
import { RefreshCw, Zap, Clock } from 'lucide-react';
import { NavigationTab } from '../types';

interface HeaderProps {
  activeTab: NavigationTab;
  onRefresh: () => void;
  isRefreshing: boolean;
  onRunDetection: () => void;
  isDetecting: boolean;
  lastUpdated?: string;
}

const TAB_TITLES: Record<NavigationTab, { title: string; subtitle: string }> = {
  overview: {
    title: 'Revenue Assurance Overview',
    subtitle: 'Comprehensive financial leakage detection, order fulfillment integrity, and cash settlement KPIs',
  },
  exceptions: {
    title: 'Revenue Leakage & Process Exceptions',
    subtitle: 'Detailed exception explorer across 12 rule detectors with substantiating evidence',
  },
  orders: {
    title: 'Sales Order Ledger',
    subtitle: 'Commercial sales orders tracked from confirmation to billing closure',
  },
  invoices: {
    title: 'Accounts Receivable Invoices',
    subtitle: 'Billed revenue ledger with tracked payment status and outstanding balances',
  },
  payments: {
    title: 'Treasury & Cash Settlements',
    subtitle: 'Ingested bank remittances and cash application status',
  },
  disputes: {
    title: 'Customer Billing Disputes',
    subtitle: 'Lodged invoice disputes under investigation and pending resolution',
  },
};

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onRefresh,
  isRefreshing,
  onRunDetection,
  isDetecting,
  lastUpdated,
}) => {
  const current = TAB_TITLES[activeTab];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-20 px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">{current.title}</h1>
        <p className="text-xs text-slate-500 mt-0.5">{current.subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {lastUpdated && (
          <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-50 px-3 py-1.5 rounded-md border border-slate-200">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Updated {lastUpdated}</span>
          </div>
        )}

        <button
          onClick={onRefresh}
          disabled={isRefreshing || isDetecting}
          className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 rounded-lg text-xs font-medium transition-colors shadow-sm disabled:opacity-50"
          title="Refresh current data from PostgreSQL"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-600' : 'text-slate-500'}`} />
          <span>Refresh</span>
        </button>

        {/* Prominent Run Detection Button */}
        <button
          onClick={onRunDetection}
          disabled={isDetecting}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold text-white transition-all shadow-sm ${
            isDetecting
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 ring-2 ring-blue-600/20'
          }`}
          title="Run all 12 rule detectors against PostgreSQL database"
        >
          {isDetecting ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span>Scanning 12 Rules...</span>
            </>
          ) : (
            <>
              <Zap className="w-3.5 h-3.5 fill-current text-amber-300" />
              <span>Run Detection</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
