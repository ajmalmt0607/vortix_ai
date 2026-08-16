import { TrendingUp, TrendingDown } from "lucide-react";
import { formatMoney, formatNumber, formatPercent } from "../../utils/format";
import EmptyState from "../common/EmptyState";

export default function BranchPerformance({ branches }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">Branch Performance</h3>
      </div>

      {!branches || branches.length === 0 ? (
        <EmptyState title="No branch data" message="No orders found for this period." />
      ) : (
        <>
          {/* Mobile: card list */}
          <div className="divide-y divide-slate-100 sm:hidden">
            {branches.map((b) => {
              const negative = b.growth_percentage < 0;
              const GrowthIcon = negative ? TrendingDown : TrendingUp;
              return (
                <div key={b.branch_id} className="p-4">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm font-medium text-slate-800">{b.branch_name}</p>
                    <span
                      className={`inline-flex flex-shrink-0 items-center gap-1 text-xs font-semibold ${
                        negative ? "text-rose-600" : "text-emerald-600"
                      }`}
                    >
                      <GrowthIcon className="h-3.5 w-3.5" />
                      {formatPercent(b.growth_percentage)}
                    </span>
                  </div>
                  <p className="mt-2.5 text-[11px] uppercase tracking-wide text-slate-400">Revenue</p>
                  <p className="text-lg font-semibold text-slate-900">{formatMoney(b.revenue)}</p>
                  <div className="mt-2.5 grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-slate-400">Orders</p>
                      <p className="text-sm font-medium text-slate-700">{formatNumber(b.orders)}</p>
                    </div>
                    <div>
                      <p className="text-[11px] uppercase tracking-wide text-slate-400">Avg Order</p>
                      <p className="text-sm font-medium text-slate-700">
                        {formatMoney(b.average_order_value)}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Desktop/tablet: table */}
          <div className="hidden overflow-x-auto sm:block">
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
                    <td className="px-5 py-3 text-right text-slate-500">
                      {formatMoney(b.average_order_value)}
                    </td>
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
          </div>
        </>
      )}
    </div>
  );
}
