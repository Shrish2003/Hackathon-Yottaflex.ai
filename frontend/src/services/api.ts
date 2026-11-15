/**
 * API service for calling backend health and diagnostic endpoints.
 */

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

export async function checkAppHealth(): Promise<{ success: boolean; data?: AppHealthResponse; error?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) {
      return { success: false, error: `HTTP ${res.status}: ${res.statusText}` };
    }
    const data = await res.json();
    return { success: true, data };
  } catch (err: any) {
    return { success: false, error: err.message || 'Network error / backend unreachable' };
  }
}

export async function checkDbHealth(): Promise<{ success: boolean; data?: DbHealthResponse; error?: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/health/db`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    const data: DbHealthResponse = await res.json();
    if (res.ok && data.connected) {
      return { success: true, data };
    }
    return {
      success: false,
      data,
      error: data.error || data.message || `HTTP ${res.status} (Database Disconnected)`,
    };
  } catch (err: any) {
    return { success: false, error: err.message || 'Network error / backend unreachable' };
  }
}
