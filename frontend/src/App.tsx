import { useState, useEffect, useCallback } from 'react';
import { RefreshCw, ShieldCheck, Activity, Terminal, ArrowRight, Layers } from 'lucide-react';
import { checkAppHealth, checkDbHealth, AppHealthResponse, DbHealthResponse } from './services/api';
import { StatusCard, ComponentStatus } from './components/StatusCard';

export function App() {
  const [appStatus, setAppStatus] = useState<ComponentStatus>('loading');
  const [appData, setAppData] = useState<AppHealthResponse | undefined>();
  const [appError, setAppError] = useState<string | undefined>();

  const [dbStatus, setDbStatus] = useState<ComponentStatus>('loading');
  const [dbData, setDbData] = useState<DbHealthResponse | undefined>();
  const [dbError, setDbError] = useState<string | undefined>();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastChecked, setLastChecked] = useState<string>('');

  const runConnectivityChecks = useCallback(async () => {
    setIsRefreshing(true);
    setAppStatus('loading');
    setDbStatus('loading');
    setAppError(undefined);
    setDbError(undefined);

    const now = new Date().toLocaleTimeString();
    setLastChecked(now);

    // 1. Check Application Health
    const appRes = await checkAppHealth();
    if (appRes.success && appRes.data) {
      setAppStatus('connected');
      setAppData(appRes.data);
    } else {
      setAppStatus('disconnected');
      setAppError(appRes.error);
    }

    // 2. Check PostgreSQL Database Health
    const dbRes = await checkDbHealth();
    if (dbRes.success && dbRes.data) {
      setDbStatus('connected');
      setDbData(dbRes.data);
    } else {
      setDbStatus('disconnected');
      setDbData(dbRes.data);
      setDbError(dbRes.error);
    }

    setIsRefreshing(false);
  }, []);

  useEffect(() => {
    runConnectivityChecks();
  }, [runConnectivityChecks]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg text-white shadow-sm">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-slate-900 text-lg leading-tight">
                O2C Revenue Assurance Platform
              </h1>
              <p className="text-xs text-slate-500 font-medium">
                Stage 1: Foundation &amp; Connectivity Verification
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <Layers className="w-3.5 h-3.5" />
              Stage 1 Active
            </span>
            <button
              onClick={runConnectivityChecks}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-medium transition-colors shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              Retry Connectivity Checks
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {/* Banner Section */}
        <div className="bg-gradient-to-r from-slate-900 to-blue-950 rounded-2xl p-6 sm:p-8 text-white shadow-md relative overflow-hidden">
          <div className="relative z-10 max-w-3xl">
            <span className="inline-block px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-mono font-semibold mb-3 border border-blue-400/30">
              ENVIRONMENT CONNECTIVITY DASHBOARD
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-2">
              Order-to-Cash (O2C) Foundation Verification
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">
              Real-time connectivity monitoring for the enterprise revenue assurance engine. All health metrics are live queries executed against the FastAPI backend and PostgreSQL database.
            </p>
          </div>
        </div>

        {/* Status Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Backend API Status */}
          <StatusCard
            title="FastAPI Backend Engine"
            iconType="server"
            status={appStatus}
            statusText={appStatus === 'connected' ? 'FastAPI 0.110+ Running' : 'API Unreachable'}
            endpoint="GET /health"
            details={appData ? {
              Application: appData.app_name,
              Environment: appData.environment,
              DebugMode: appData.debug ? 'Enabled' : 'Disabled',
            } : undefined}
            errorMessage={appError}
            lastChecked={lastChecked}
          />

          {/* PostgreSQL Database Status */}
          <StatusCard
            title="PostgreSQL Relational DB"
            iconType="database"
            status={dbStatus}
            statusText={dbStatus === 'connected' ? 'PostgreSQL Active (SELECT 1 Verified)' : 'Database Disconnected'}
            endpoint="GET /health/db"
            details={dbData ? {
              Database: dbData.database || 'o2c_revenue_db',
              QueryType: 'SELECT 1 (Real DB Query)',
              Result: dbData.connected ? 'Success (200 OK)' : 'Failed (503 Service Unavailable)',
            } : undefined}
            errorMessage={dbError}
            lastChecked={lastChecked}
          />
        </div>

        {/* Stage 1 Checklist & Guidance */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900 text-base">Stage 1 Foundation Status</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-800 block mb-1">1. Frontend Stack</span>
              <p className="text-slate-600">React 18, TypeScript, Vite, Tailwind CSS running locally on port 5173.</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-800 block mb-1">2. Backend Stack</span>
              <p className="text-slate-600">FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn on port 8000.</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <span className="font-semibold text-slate-800 block mb-1">3. Database Target</span>
              <p className="text-slate-600">PostgreSQL 15+ target database: <code className="font-mono text-blue-600 font-bold">o2c_revenue_db</code>.</p>
            </div>
          </div>

          {dbStatus === 'disconnected' && (
            <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
              <div className="flex items-center gap-2 font-semibold mb-1 text-amber-950">
                <Terminal className="w-4 h-4" /> Next Steps: PostgreSQL Configuration Required
              </div>
              <p className="mb-2 text-amber-800">
                PostgreSQL is currently not accepting connections or requires password configuration. Follow the manual checklist in <code className="font-mono font-bold">docs/STAGE_1_COMPLETION_REPORT.md</code> to start the PostgreSQL service and set your database password in <code className="font-mono font-bold">backend/.env</code>.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <span>O2C Revenue Assurance Platform &copy; 2026. All rights reserved.</span>
          <div className="flex items-center gap-4">
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center gap-1 font-medium">
              Backend Swagger Docs <ArrowRight className="w-3 h-3" />
            </a>
            <a href="http://localhost:8000/health" target="_blank" rel="noreferrer" className="text-blue-600 hover:underline flex items-center gap-1 font-medium">
              Raw Health API <ArrowRight className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
