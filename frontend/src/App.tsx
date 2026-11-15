import { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle2,
  X,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';
import { NavigationTab, DetectionRunResult } from './types';
import { checkDbHealth, triggerDetectionRun, getDashboardSummary } from './services/api';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ExceptionDetailModal } from './components/ExceptionDetailModal';
import {
  OverviewPage,
  ExceptionsPage,
  OrdersPage,
  InvoicesPage,
  PaymentsPage,
  DisputesPage,
} from './pages';
import { formatINR } from './utils/formatters';

export function App() {
  const getInitialTab = (): NavigationTab => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab') as NavigationTab;
    if (['overview', 'exceptions', 'orders', 'invoices', 'payments', 'disputes'].includes(tabParam)) {
      return tabParam;
    }
    return 'overview';
  };

  const getInitialExceptionId = (): string | null => {
    const params = new URLSearchParams(window.location.search);
    return params.get('exceptionId');
  };

  const [activeTab, setActiveTab] = useState<NavigationTab>(getInitialTab);
  const [dbConnected, setDbConnected] = useState<boolean>(true);
  const [exceptionCount, setExceptionCount] = useState<number>(0);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isDetecting, setIsDetecting] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  // Cross-page navigation filters
  const [exceptionFilterSeverity, setExceptionFilterSeverity] = useState<string | undefined>();
  const [exceptionFilterAnomalyType, setExceptionFilterAnomalyType] = useState<string | undefined>();

  // Modal detail view
  const [selectedExceptionId, setSelectedExceptionId] = useState<string | null>(getInitialExceptionId);

  // Global detection notification banner
  const [detectionNotice, setDetectionNotice] = useState<{
    type: 'success' | 'error';
    message: string;
    detail?: string;
  } | null>(null);

  // Check database health and load initial badges
  const checkHealthAndBadges = useCallback(async () => {
    try {
      const dbRes = await checkDbHealth();
      setDbConnected(dbRes.success);

      const summary = await getDashboardSummary();
      setExceptionCount(summary.total_detected_exceptions);
      setLastUpdated(new Date().toLocaleTimeString('en-IN'));
    } catch {
      // Backend might still be starting
    }
  }, []);

  useEffect(() => {
    checkHealthAndBadges();
  }, [checkHealthAndBadges, refreshTrigger]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshTrigger((prev) => prev + 1);
    await checkHealthAndBadges();
    setIsRefreshing(false);
  };

  const handleRunDetection = async () => {
    if (isDetecting) return; // Prevent repeated submissions
    setIsDetecting(true);
    setDetectionNotice(null);

    try {
      const result: DetectionRunResult = await triggerDetectionRun();
      setDetectionNotice({
        type: 'success',
        message: `Detection Scan Complete: ${result.total_exceptions} exceptions identified across 12 rule detectors.`,
        detail: `Execution time: ${result.duration_seconds.toFixed(2)}s | Total quantified leakage: ${formatINR(
          result.total_financial_leakage_inr
        )} | Persisted evidence: ${result.total_evidence_records} records.`,
      });
      // Trigger full data refresh
      setRefreshTrigger((prev) => prev + 1);
      setExceptionCount(result.total_exceptions);
      setLastUpdated(new Date().toLocaleTimeString('en-IN'));
    } catch (err: any) {
      setDetectionNotice({
        type: 'error',
        message: 'Detection Engine execution failed.',
        detail: err.message || 'An unexpected error occurred during rule execution.',
      });
    } finally {
      setIsDetecting(false);
    }
  };

  const handleNavigateTab = (
    tab: NavigationTab,
    filters?: { severity?: string; anomaly_type?: string }
  ) => {
    if (filters) {
      setExceptionFilterSeverity(filters.severity);
      setExceptionFilterAnomalyType(filters.anomaly_type);
    } else {
      setExceptionFilterSeverity(undefined);
      setExceptionFilterAnomalyType(undefined);
    }
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-row font-sans text-slate-800 antialiased selection:bg-blue-500 selection:text-white">
      {/* Fixed Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={(tab) => handleNavigateTab(tab)}
        exceptionCount={exceptionCount}
        dbConnected={dbConnected}
      />

      {/* Main Layout Area */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* Sticky Header */}
        <Header
          activeTab={activeTab}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          onRunDetection={handleRunDetection}
          isDetecting={isDetecting}
          lastUpdated={lastUpdated}
        />

        {/* Global Notification Banner for Detection Action */}
        {detectionNotice && (
          <div className="px-8 pt-4 animate-in fade-in slide-in-from-top-2 duration-200">
            <div
              className={`p-4 rounded-xl border flex items-start justify-between gap-3 shadow-sm ${
                detectionNotice.type === 'success'
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                  : 'bg-rose-50 border-rose-200 text-rose-900'
              }`}
            >
              <div className="flex items-start gap-3">
                {detectionNotice.type === 'success' ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="text-xs">
                  <span className="font-bold block">{detectionNotice.message}</span>
                  {detectionNotice.detail && (
                    <span className="text-slate-600 mt-0.5 block">{detectionNotice.detail}</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setDetectionNotice(null)}
                className="text-slate-400 hover:text-slate-700 p-1 rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Active Tab View */}
        <main className="flex-1 pb-16">
          {activeTab === 'overview' && (
            <OverviewPage
              onNavigateTab={handleNavigateTab}
              onSelectException={(id) => setSelectedExceptionId(id)}
              refreshTrigger={refreshTrigger}
            />
          )}

          {activeTab === 'exceptions' && (
            <ExceptionsPage
              onSelectException={(id) => setSelectedExceptionId(id)}
              initialSeverity={exceptionFilterSeverity}
              initialAnomalyType={exceptionFilterAnomalyType}
              refreshTrigger={refreshTrigger}
            />
          )}

          {activeTab === 'orders' && <OrdersPage refreshTrigger={refreshTrigger} />}

          {activeTab === 'invoices' && <InvoicesPage refreshTrigger={refreshTrigger} />}

          {activeTab === 'payments' && <PaymentsPage refreshTrigger={refreshTrigger} />}

          {activeTab === 'disputes' && <DisputesPage refreshTrigger={refreshTrigger} />}
        </main>

        {/* Enterprise Footer */}
        <footer className="bg-white border-t border-slate-200 py-3.5 px-8 mt-auto flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">RevAssure O2C</span>
            <span>&bull;</span>
            <span>Enterprise Revenue Assurance &amp; Leakage Detection Platform</span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-slate-400 font-mono">FastAPI + React 18 + PostgreSQL</span>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 hover:underline inline-flex items-center gap-1 font-medium"
            >
              API Swagger <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </footer>
      </div>

      {/* Exception Detail Dossier Modal */}
      <ExceptionDetailModal
        exceptionId={selectedExceptionId}
        onClose={() => setSelectedExceptionId(null)}
      />
    </div>
  );
}

export default App;
