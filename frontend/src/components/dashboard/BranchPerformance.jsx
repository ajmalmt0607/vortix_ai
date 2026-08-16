import { formatMoney, formatNumber, formatPercent } from "../../utils/format";
import EmptyState from "../common/EmptyState";

export default function BranchPerformance({ branches }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">Branch Performance</h3>
      </div>
      <div className="overflow-x-auto">
        {!branches || branches.length === 0 ? (
          <EmptyState title="No branch data" message="No orders found for this period." />
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-400">
                <th className="px-5 py-2 font-medium">Branch</th>
                <th className="px-5 py-2 text-right font-medium">Revenue</th>
                <th className="px-5 py-2 text-right font-medium">Orders</th>
                <th className="px-5 py-2 text-right font-medium">AOV</th>
                <th className="px-5 py-2 text-right font-medium">Growth</th>
              </tr>
            </thead>
            <tbody>
              {branches.map((b) => (
                <tr key={b.branch_id} className="border-t border-slate-50">
                  <td className="px-5 py-3 font-medium text-slate-700">{b.branch_name}</td>
                  <td className="px-5 py-3 text-right text-slate-700">{formatMoney(b.revenue)}</td>
                  <td className="px-5 py-3 text-right text-slate-500">{formatNumber(b.orders)}</td>
                  <td className="px-5 py-3 text-right text-slate-500">{formatMoney(b.average_order_value)}</td>
                  <td
                    className={`px-5 py-3 text-right font-medium ${
                      b.growth_percentage < 0 ? "text-rose-600" : "text-emerald-600"
                    }`}
                  >
                    {formatPercent(b.growth_percentage)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
