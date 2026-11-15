/**
 * Unified TypeScript type definitions for O2C Revenue Assurance Platform.
 */

export type NavigationTab = 'overview' | 'exceptions' | 'orders' | 'invoices' | 'payments' | 'disputes';

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface DashboardSummary {
  total_accounts: intOrNum;
  total_quotes: intOrNum;
  total_sales_orders: intOrNum;
  total_shipments: intOrNum;
  total_invoices: intOrNum;
  total_payments: intOrNum;
  total_detected_exceptions: intOrNum;
  total_identified_leakage_amount: number;
  exception_counts_by_severity: Record<string, number>;
  exception_counts_by_anomaly_type: Record<string, number>;
}

type intOrNum = number;

export interface EvidenceItem {
  evidence_id: string;
  exception_id: string;
  evidence_type: string;
  source_table: string;
  source_id: string;
  conflicting_source_table?: string | null;
  conflicting_source_id?: string | null;
  expected_value?: number | null;
  actual_value?: number | null;
  discrepancy_delta?: number | null;
  evidence_payload: Record<string, any>;
  created_at: string;
}

export interface ExceptionRecord {
  exception_id: string;
  issue_type: string;
  severity: SeverityLevel | string;
  entity_type: string;
  entity_id: string;
  business_id: string;
  account_id?: string | null;
  order_id?: string | null;
  invoice_id?: string | null;
  payment_id?: string | null;
  dispute_id?: string | null;
  leakage_amount?: number | null;
  detected_at: string;
  explanation: string;
  recommended_action: string;
  evidence_count: number;
}

export interface ExceptionDetail extends ExceptionRecord {
  evidence_items: EvidenceItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface OrderItem {
  order_id: string;
  business_id: string;
  account_id: string;
  quote_id?: string | null;
  status: string;
  total_order_value: number;
  currency: string;
  order_date: string;
  created_at: string;
}

export interface InvoiceItem {
  invoice_id: string;
  business_id: string;
  order_id: string;
  account_id: string;
  status: string;
  total_invoiced_amount: number;
  paid_amount: number;
  outstanding_balance: number;
  currency: string;
  issue_date: string;
  due_date: string;
  created_at: string;
}

export interface PaymentItem {
  payment_id: string;
  business_id: string;
  account_id: string;
  payment_method: string;
  payment_reference: string;
  amount_received: number;
  amount_allocated: number;
  unallocated_amount: number;
  currency: string;
  status: string;
  payment_date: string;
  created_at: string;
}

export interface DisputeItem {
  dispute_id: string;
  business_id: string;
  invoice_id: string;
  dispute_reason: string;
  disputed_amount: number;
  status: string;
  lodged_at: string;
  resolved_at?: string | null;
  created_at: string;
}

export interface AccountItem {
  account_id: string;
  account_number: string;
  account_name: string;
  credit_limit: number;
  payment_terms: string;
  currency: string;
  status: string;
  created_at: string;
}

export interface DetectionRunResult {
  status: string;
  execution_timestamp: string;
  simulation_as_of_date: string;
  duration_seconds: number;
  total_exceptions: number;
  total_evidence_records: number;
  total_financial_leakage_inr: number;
  by_issue_type: Record<string, number>;
  by_severity: Record<string, number>;
}
