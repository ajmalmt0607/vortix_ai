import { useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";

const STATUS_OPTIONS = ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"];
const TYPE_OPTIONS = ["DINE_IN", "TAKEAWAY", "DELIVERY"];
const TYPE_LABELS = { DINE_IN: "Dine-in", TAKEAWAY: "Takeaway", DELIVERY: "Delivery" };
const FILTER_KEYS = ["branch", "start_date", "end_date", "status", "order_type"];

function titleCase(value) {
  return value.charAt(0) + value.slice(1).toLowerCase();
}

export default function OrdersFilters({ branches, filters, onChange }) {
  const [expanded, setExpanded] = useState(false);
  const activeCount = FILTER_KEYS.filter((key) => filters[key]).length;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3.5 sm:p-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={filters.search || ""}
            onChange={(e) => onChange({ search: e.target.value || null })}
            placeholder="Order number or customer..."
            className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          aria-expanded={expanded}
          className={`relative flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg border transition-colors sm:hidden ${
            expanded ? "border-indigo-200 bg-indigo-50 text-indigo-600" : "border-slate-200 text-slate-500"
          }`}
        >
          <SlidersHorizontal className="h-4 w-4" />
          {activeCount > 0 && (
            <span className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-semibold text-white">
              {activeCount}
            </span>
          )}
        </button>
      </div>

      <div
        className={`${
          expanded ? "mt-3 grid" : "hidden"
        } grid-cols-2 gap-3 sm:mt-3 sm:grid sm:grid-cols-3 lg:grid-cols-5`}
      >
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Branch</label>
          <select
            value={filters.branch || ""}
            onChange={(e) => onChange({ branch: e.target.value || null })}
            className="w-full rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All Branches</option>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Start date</label>
          <input
            type="date"
            value={filters.start_date || ""}
            onChange={(e) => onChange({ start_date: e.target.value || null })}
            className="w-full rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">End date</label>
          <input
            type="date"
            value={filters.end_date || ""}
            onChange={(e) => onChange({ end_date: e.target.value || null })}
            className="w-full rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Status</label>
          <select
            value={filters.status || ""}
            onChange={(e) => onChange({ status: e.target.value || null })}
            className="w-full rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {titleCase(s)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Order type</label>
          <select
            value={filters.order_type || ""}
            onChange={(e) => onChange({ order_type: e.target.value || null })}
            className="w-full rounded-lg border border-slate-200 px-2.5 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All</option>
            {TYPE_OPTIONS.map((t) => (
              <option key={t} value={t}>
                {TYPE_LABELS[t]}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
