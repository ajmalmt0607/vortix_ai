import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatMoney, formatDateShort } from "../../utils/format";
import EmptyState from "../common/EmptyState";

function getNiceMax(max) {
  if (max <= 0) return 100;
  const magnitude = Math.pow(10, Math.floor(Math.log10(max)));
  const normalized = max / magnitude;
  let niceNormalized;
  if (normalized <= 1) niceNormalized = 1;
  else if (normalized <= 2) niceNormalized = 2;
  else if (normalized <= 5) niceNormalized = 5;
  else niceNormalized = 10;
  return niceNormalized * magnitude;
}

function buildTicks(maxValue, count = 5) {
  const niceMax = getNiceMax(maxValue || 1);
  const step = niceMax / (count - 1);
  return Array.from({ length: count }, (_, i) => Math.round(step * i));
}

function formatAxisValue(value) {
  if (value === 0) return "0";
  if (value >= 1000) {
    const k = value / 1000;
    return `${Number.isInteger(k) ? k : k.toFixed(1)}k`;
  }
  return `${value}`;
}

export default function RevenueChart({ trend }) {
  if (!trend || trend.length === 0) {
    return (
      <div className="h-full rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <h3 className="mb-4 text-sm font-semibold text-slate-900">Revenue Trend</h3>
        <EmptyState title="No sales data" message="No orders found for this period." />
      </div>
    );
  }

  const chartData = trend.map((row) => ({ ...row, label: formatDateShort(row.date) }));
  const maxRevenue = Math.max(...chartData.map((d) => d.revenue), 0);
  const ticks = buildTicks(maxRevenue, 5);

  return (
    <div className="h-full rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <h3 className="mb-4 text-sm font-semibold text-slate-900">Revenue Trend</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
          <YAxis
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            axisLine={false}
            tickLine={false}
            width={40}
            domain={[0, ticks[ticks.length - 1]]}
            ticks={ticks}
            tickFormatter={formatAxisValue}
          />
          <Tooltip
            formatter={(value) => [formatMoney(value), "Revenue"]}
            labelFormatter={(label, payload) => payload?.[0]?.payload?.date || label}
            contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0", fontSize: 12 }}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#4f46e5"
            strokeWidth={2}
            fill="url(#revenueFill)"
            name="Revenue"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
