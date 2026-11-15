/**
 * Formatting and visual helper utilities for O2C Revenue Assurance Platform.
 */

/**
 * Format a numeric amount into Indian Rupee (INR) representation with ₹ symbol.
 */
export function formatINR(amount: number | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '₹0.00';
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format compact numbers for high values (e.g. 1.2M or 1.2 Cr).
 */
export function formatCompactINR(amount: number | null | undefined): string {
  if (!amount || isNaN(amount)) return '₹0';
  if (Math.abs(amount) >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`;
  }
  if (Math.abs(amount) >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} Lakh`;
  }
  return formatINR(amount);
}

/**
 * Format ISO datetime string to clean readable date & time.
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return d.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
}

/**
 * Format ISO date string to date-only.
 */
export function formatDateOnly(dateString: string | null | undefined): string {
  if (!dateString) return '-';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return d.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}

/**
 * Convert raw uppercase anomaly issue type to clean title string.
 */
export function formatAnomalyType(type: string): string {
  if (!type) return '-';
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Badge styling according to exception severity.
 */
export function getSeverityStyle(severity: string): { bg: string; text: string; border: string; dot: string } {
  switch (severity?.toUpperCase()) {
    case 'CRITICAL':
      return {
        bg: 'bg-rose-50',
        text: 'text-rose-700',
        border: 'border-rose-200',
        dot: 'bg-rose-500',
      };
    case 'HIGH':
      return {
        bg: 'bg-orange-50',
        text: 'text-orange-700',
        border: 'border-orange-200',
        dot: 'bg-orange-500',
      };
    case 'MEDIUM':
      return {
        bg: 'bg-amber-50',
        text: 'text-amber-700',
        border: 'border-amber-200',
        dot: 'bg-amber-500',
      };
    case 'LOW':
      return {
        bg: 'bg-blue-50',
        text: 'text-blue-700',
        border: 'border-blue-200',
        dot: 'bg-blue-500',
      };
    default:
      return {
        bg: 'bg-slate-50',
        text: 'text-slate-700',
        border: 'border-slate-200',
        dot: 'bg-slate-400',
      };
  }
}

/**
 * Badge styling according to transaction / entity status.
 */
export function getStatusStyle(status: string): { bg: string; text: string; border: string } {
  switch (status?.toUpperCase()) {
    case 'CLOSED':
    case 'PAID':
    case 'RESOLVED':
    case 'ALLOCATED':
    case 'CONFIRMED':
    case 'ACTIVE':
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' };
    case 'PARTIALLY_PAID':
    case 'PARTIALLY_ALLOCATED':
    case 'UNDER_INVESTIGATION':
    case 'INVESTIGATING':
    case 'SHIPPED':
      return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' };
    case 'OPEN':
    case 'DRAFT':
    case 'ISSUED':
    case 'RECEIVED':
    case 'LODGED':
      return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' };
    case 'CANCELLED':
    case 'FAILED':
    case 'REJECTED':
      return { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' };
    default:
      return { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' };
  }
}
