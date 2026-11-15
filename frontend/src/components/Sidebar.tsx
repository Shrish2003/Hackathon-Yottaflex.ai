import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  ShoppingCart,
  FileText,
  CreditCard,
  AlertOctagon,
  ShieldCheck,
  Database,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { NavigationTab } from '../types';

interface SidebarProps {
  activeTab: NavigationTab;
  onTabChange: (tab: NavigationTab) => void;
  exceptionCount?: number;
  dbConnected?: boolean;
}

interface NavItem {
  id: NavigationTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number | string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  exceptionCount,
  dbConnected = true,
}) => {
  const navItems: NavItem[] = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'exceptions', label: 'Exceptions', icon: AlertTriangle, badge: exceptionCount },
    { id: 'orders', label: 'Sales Orders', icon: ShoppingCart },
    { id: 'invoices', label: 'Invoices', icon: FileText },
    { id: 'payments', label: 'Payments', icon: CreditCard },
    { id: 'disputes', label: 'Disputes', icon: AlertOctagon },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800/80">
        <div className="p-2 bg-blue-600 rounded-lg text-white shadow-sm flex items-center justify-center">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-white text-sm tracking-tight block">
            RevAssure O2C
          </span>
          <span className="text-[11px] text-slate-400 font-medium block">
            Revenue Assurance Platform
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-6 px-3 space-y-1">
        <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Core Assurance
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm font-semibold'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && Number(item.badge) > 0 && (
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    isActive
                      ? 'bg-blue-800/80 text-blue-100'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Database & Environment Status Footnote */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 text-xs">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] text-slate-400 font-medium">Target Database</span>
          <span className="font-mono text-[11px] text-slate-300">o2c_revenue_db</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>PostgreSQL 18</span>
          </div>
          <span
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
              dbConnected
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/50'
                : 'bg-rose-950 text-rose-400 border border-rose-800/50'
            }`}
          >
            {dbConnected ? (
              <>
                <CheckCircle2 className="w-2.5 h-2.5" /> Live
              </>
            ) : (
              <>
                <XCircle className="w-2.5 h-2.5" /> Offline
              </>
            )}
          </span>
        </div>
      </div>
    </aside>
  );
};
