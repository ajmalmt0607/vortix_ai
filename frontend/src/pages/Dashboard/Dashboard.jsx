import { useEffect, useMemo, useState } from "react";
import { getPresetRange } from "../../utils/dateRange";
import { useDashboard } from "../../hooks/useDashboard";
import { useBranches } from "../../hooks/useBranches";
import DashboardFilters from "../../components/dashboard/DashboardFilters";
import KpiCards from "../../components/dashboard/KpiCards";
import RevenueChart from "../../components/dashboard/RevenueChart";
import OrderTypeChart from "../../components/dashboard/OrderTypeChart";
import TopProducts from "../../components/dashboard/TopProducts";
import BranchPerformance from "../../components/dashboard/BranchPerformance";
import InsightsPanel from "../../components/dashboard/InsightsPanel";
import LoadingState from "../../components/common/LoadingState";
import ErrorState from "../../components/common/ErrorState";

export default function Dashboard() {
  const [preset, setPreset] = useState("30d");
  const [branchId, setBranchId] = useState(null);
  const [range, setRange] = useState(() => getPresetRange("30d"));

  const params = useMemo(
    () => ({ branch: branchId, start_date: range.start_date, end_date: range.end_date }),
    [branchId, range.start_date, range.end_date]
  );

  const { data, loading, error, reload } = useDashboard(params);
  const { branches, registerFromDashboard } = useBranches();

  useEffect(() => {
    if (data && !branchId) {
      registerFromDashboard(data.branch_performance);
    }
  }, [data, branchId, registerFromDashboard]);

  function handlePresetChange(key) {
    setPreset(key);
    setRange(getPresetRange(key));
  }

  function handleCustomDateChange(start, end) {
    setPreset(null);
    setRange({ start_date: start, end_date: end });
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">Overview of your restaurant's performance</p>
      </div>

      <DashboardFilters
        branches={branches}
        branchId={branchId}
        onBranchChange={setBranchId}
        preset={preset}
        onPresetChange={handlePresetChange}
        startDate={range.start_date}
        endDate={range.end_date}
        onCustomDateChange={handleCustomDateChange}
      />

      {loading && <LoadingState message="Loading dashboard..." />}
      {!loading && error && <ErrorState message={error} onRetry={reload} />}

      {!loading && !error && data && (
        <>
          <KpiCards summary={data.summary} comparison={data.comparison} />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <RevenueChart trend={data.sales_trend} />
            </div>
            <OrderTypeChart orderTypes={data.order_types} />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <TopProducts products={data.top_products} title="Top Selling Items" />
            <TopProducts products={data.bottom_products} title="Needs Attention" />
          </div>

          <BranchPerformance branches={data.branch_performance} />

          <InsightsPanel insights={data.insights} />
        </>
      )}
    </div>
  );
}
