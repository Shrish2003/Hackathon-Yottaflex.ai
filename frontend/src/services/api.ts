/**
 * Enterprise API client for O2C Revenue Assurance Platform.
 * Communicates with FastAPI backend endpoints.
 */

import {
  DashboardSummary,
  PaginatedResponse,
  ExceptionRecord,
  ExceptionDetail,
  OrderItem,
  InvoiceItem,
  PaymentItem,
  DisputeItem,
  DetectionRunResult,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface AppHealthResponse {
  status: string;
  app_name: string;
  environment: string;
  debug: boolean;
}

export interface DbHealthResponse {
  connected: boolean;
  status: string;
  database: string;
  message?: string;
  error?: string;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson && errJson.detail) {
        errorDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

/**
 * Health check endpoints.
 */
export async function checkAppHealth(): Promise<{ success: boolean; data?: AppHealthResponse; error?: string }> {
  try {
    const data = await request<AppHealthResponse>('/health');
    return { success: true, data };
  } catch (err: any) {
    return { success: false, error: err.message || 'API unreachable' };
  }
}

export async function checkDbHealth(): Promise<{ success: boolean; data?: DbHealthResponse; error?: string }> {
  try {
    const data = await request<DbHealthResponse>('/health/db');
    return { success: data.connected, data, error: data.connected ? undefined : (data.error || 'Database unavailable') };
  } catch (err: any) {
    return { success: false, error: err.message || 'Database health check failed' };
  }
}

/**
 * Dashboard Summary API.
 */
export async function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>('/api/dashboard/summary');
}

/**
 * Exceptions APIs.
 */
export interface ExceptionFilters {
  page?: number;
  limit?: number;
  severity?: string;
  anomaly_type?: string;
  entity_type?: string;
  search?: string;
}

export async function getExceptions(filters: ExceptionFilters = {}): Promise<PaginatedResponse<ExceptionRecord>> {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.severity && filters.severity !== 'ALL') params.append('severity', filters.severity);
  if (filters.anomaly_type && filters.anomaly_type !== 'ALL') params.append('anomaly_type', filters.anomaly_type);
  if (filters.entity_type && filters.entity_type !== 'ALL') params.append('entity_type', filters.entity_type);
  if (filters.search) params.append('search', filters.search.trim());

  const queryString = params.toString();
  return request<PaginatedResponse<ExceptionRecord>>(`/api/exceptions${queryString ? `?${queryString}` : ''}`);
}

export async function getExceptionDetail(exceptionId: string): Promise<ExceptionDetail> {
  return request<ExceptionDetail>(`/api/exceptions/${exceptionId}`);
}

/**
 * Transaction APIs: Orders, Invoices, Payments, Disputes.
 */
export interface TransactionFilters {
  page?: number;
  limit?: number;
  status?: string;
  search?: string;
}

export async function getOrders(filters: TransactionFilters = {}): Promise<PaginatedResponse<OrderItem>> {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search.trim());

  const queryString = params.toString();
  return request<PaginatedResponse<OrderItem>>(`/api/orders${queryString ? `?${queryString}` : ''}`);
}

export async function getInvoices(filters: TransactionFilters = {}): Promise<PaginatedResponse<InvoiceItem>> {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search.trim());

  const queryString = params.toString();
  return request<PaginatedResponse<InvoiceItem>>(`/api/invoices${queryString ? `?${queryString}` : ''}`);
}

export async function getPayments(filters: TransactionFilters = {}): Promise<PaginatedResponse<PaymentItem>> {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search.trim());

  const queryString = params.toString();
  return request<PaginatedResponse<PaymentItem>>(`/api/payments${queryString ? `?${queryString}` : ''}`);
}

export async function getDisputes(filters: TransactionFilters = {}): Promise<PaginatedResponse<DisputeItem>> {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search.trim());

  const queryString = params.toString();
  return request<PaginatedResponse<DisputeItem>>(`/api/disputes${queryString ? `?${queryString}` : ''}`);
}

/**
 * Detection Execution API.
 */
export async function triggerDetectionRun(): Promise<DetectionRunResult> {
  return request<DetectionRunResult>('/api/detection/run', {
    method: 'POST',
  });
}
