import { formatMoney, formatNumber } from "../../utils/format";
import EmptyState from "../common/EmptyState";

export default function TopProducts({ products, title }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      </div>
      <div className="p-2">
        {!products || products.length === 0 ? (
          <EmptyState title="No product data" message="No sales found for this period." />
        ) : (
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
        )}
      </div>
    </div>
  );
}
