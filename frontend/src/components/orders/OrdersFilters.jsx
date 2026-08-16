import { Search } from "lucide-react";

const STATUS_OPTIONS = ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"];
const TYPE_OPTIONS = ["DINE_IN", "TAKEAWAY", "DELIVERY"];
const TYPE_LABELS = { DINE_IN: "Dine-in", TAKEAWAY: "Takeaway", DELIVERY: "Delivery" };

function titleCase(value) {
  return value.charAt(0) + value.slice(1).toLowerCase();
}

export default function OrdersFilters({ branches, filters, onChange }) {
  return (
    <div className="grid grid-cols-1 gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-2 lg:grid-cols-5">
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-500">Branch</label>
        <select
          value={filters.branch || ""}
          onChange={(e) => onChange({ branch: e.target.value || null })}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-slate-500">End date</label>
        <input
          type="date"
          value={filters.end_date || ""}
          onChange={(e) => onChange({ end_date: e.target.value || null })}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-slate-500">Status</label>
        <select
          value={filters.status || ""}
          onChange={(e) => onChange({ status: e.target.value || null })}
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
          className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All</option>
          {TYPE_OPTIONS.map((t) => (
            <option key={t} value={t}>
              {TYPE_LABELS[t]}
            </option>
          ))}
        </select>
      </div>

      <div className="sm:col-span-2 lg:col-span-5">
        <label className="mb-1 block text-xs font-medium text-slate-500">Search</label>
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={filters.search || ""}
            onChange={(e) => onChange({ search: e.target.value || null })}
            placeholder="Order number or customer name..."
            className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>
    </div>
  );
}
