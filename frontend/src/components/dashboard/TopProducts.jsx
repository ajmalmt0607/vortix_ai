import { formatMoney, formatNumber } from "../../utils/format";
import EmptyState from "../common/EmptyState";

const MEDALS = ["🥇", "🥈", "🥉"];

export default function TopProducts({ products, title, variant = "top" }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      </div>

      {!products || products.length === 0 ? (
        <div className="p-2">
          <EmptyState title="No product data" message="No sales found for this period." />
        </div>
      ) : (
        <>
          {/* Mobile: compact list */}
          <div className="divide-y divide-slate-50 sm:hidden">
            {products.map((p, idx) => (
              <div key={p.product_id} className="flex items-center justify-between gap-3 px-4 py-3">
                <div className="flex min-w-0 items-center gap-2.5">
                  {variant === "top" && MEDALS[idx] ? (
                    <span className="flex-shrink-0 text-base leading-none">{MEDALS[idx]}</span>
                  ) : (
                    <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-medium text-slate-500">
                      {idx + 1}
                    </span>
                  )}
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-800">{p.product_name}</p>
                    <p className="text-xs text-slate-400">
                      {formatNumber(p.quantity)} sold · {formatMoney(p.revenue)}
                    </p>
                  </div>
                </div>
                {variant === "bottom" && (
                  <span className="flex-shrink-0 rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-medium text-amber-700">
                    Low volume
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Desktop/tablet: table */}
          <div className="hidden p-2 sm:block">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-400">
                  <th className="px-3 py-2 font-medium">Product</th>
                  <th className="px-3 py-2 text-right font-medium">Qty</th>
                  <th className="px-3 py-2 text-right font-medium">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.product_id} className="border-t border-slate-50">
                    <td className="px-3 py-2.5 font-medium text-slate-700">{p.product_name}</td>
                    <td className="px-3 py-2.5 text-right text-slate-500">{formatNumber(p.quantity)}</td>
                    <td className="px-3 py-2.5 text-right text-slate-700">{formatMoney(p.revenue)}</td>
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
