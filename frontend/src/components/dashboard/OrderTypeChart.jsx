import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { formatNumber } from "../../utils/format";
import EmptyState from "../common/EmptyState";

const COLORS = { DINE_IN: "#4f46e5", TAKEAWAY: "#0ea5e9", DELIVERY: "#f59e0b" };
const LABELS = { DINE_IN: "Dine-in", TAKEAWAY: "Takeaway", DELIVERY: "Delivery" };

export default function OrderTypeChart({ orderTypes }) {
  if (!orderTypes || orderTypes.length === 0) {
    return (
      <div className="h-full rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <h3 className="mb-4 text-sm font-semibold text-slate-900">Order Types</h3>
        <EmptyState title="No orders" message="No orders found for this period." />
      </div>
    );
  }

  const data = orderTypes.map((t) => ({
    ...t,
    label: LABELS[t.type] || t.type,
    color: COLORS[t.type] || "#94a3b8",
  }));

  return (
    <div className="h-full rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <h3 className="mb-4 text-sm font-semibold text-slate-900">Order Types</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="orders" nameKey="label" innerRadius={55} outerRadius={85} paddingAngle={2}>
            {data.map((entry) => (
              <Cell key={entry.type} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, _name, props) => [
              `${formatNumber(value)} orders (${props.payload.percentage}%)`,
              props.payload.label,
            ]}
            contentStyle={{ borderRadius: 8, borderColor: "#e2e8f0", fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
      <ul className="mt-2 space-y-1.5">
        {data.map((row) => (
          <li key={row.type} className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-2 text-slate-600">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: row.color }} />
              {row.label}
            </span>
            <span className="text-slate-500">
              {formatNumber(row.orders)} · {row.percentage}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
