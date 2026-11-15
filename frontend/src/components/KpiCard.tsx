import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'danger' | 'warning' | 'success' | 'info';
  badge?: string;
}

const VARIANT_STYLES = {
  default: {
    iconBg: 'bg-slate-100 text-slate-700',
    border: 'border-slate-200',
    valueText: 'text-slate-900',
  },
  danger: {
    iconBg: 'bg-rose-100 text-rose-700',
    border: 'border-rose-200 shadow-rose-50',
    valueText: 'text-rose-700',
  },
  warning: {
    iconBg: 'bg-amber-100 text-amber-700',
    border: 'border-amber-200 shadow-amber-50',
    valueText: 'text-amber-800',
  },
  success: {
    iconBg: 'bg-emerald-100 text-emerald-700',
    border: 'border-emerald-200 shadow-emerald-50',
    valueText: 'text-emerald-800',
  },
  info: {
    iconBg: 'bg-blue-100 text-blue-700',
    border: 'border-blue-200 shadow-blue-50',
    valueText: 'text-blue-800',
  },
};

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
  badge,
}) => {
  const styles = VARIANT_STYLES[variant];

  return (
    <div className={`bg-white rounded-xl border ${styles.border} p-5 shadow-sm transition-all hover:shadow-md`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg ${styles.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <div className={`text-2xl font-bold tracking-tight ${styles.valueText}`}>
          {value}
        </div>
        {badge && (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-700">
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="text-xs text-slate-500 mt-2 font-medium leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
};
