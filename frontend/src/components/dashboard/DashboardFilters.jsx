const PERIOD_OPTIONS = [
  { key: "today", label: "Today" },
  { key: "yesterday", label: "Yesterday" },
  { key: "7d", label: "7 Days" },
  { key: "30d", label: "30 Days" },
  { key: "custom", label: "Custom Range" },
];

export default function DashboardFilters({
  branches,
  branchId,
  onBranchChange,
  preset,
  onPresetChange,
  startDate,
  endDate,
  onCustomDateChange,
}) {
  const isCustom = preset === "custom";

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-3.5 sm:p-4">
      <div className="grid grid-cols-2 gap-3 sm:flex sm:flex-wrap sm:items-end sm:justify-between sm:gap-4">
        <div>
          <label className="mb-1 block text-[11px] font-medium text-slate-500">Branch</label>
          <select
            value={branchId || ""}
            onChange={(e) => onBranchChange(e.target.value || null)}
            className="w-full rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:w-48"
          >
            <option value="">All Branches</option>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>

        {/* Compact period select — mobile only */}
        <div className="sm:hidden">
          <label className="mb-1 block text-[11px] font-medium text-slate-500">Period</label>
          <select
            value={preset}
            onChange={(e) => onPresetChange(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-white px-2.5 py-2 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {PERIOD_OPTIONS.map((p) => (
              <option key={p.key} value={p.key}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        {/* Period pill buttons — tablet/desktop */}
        <div className="hidden sm:flex sm:flex-wrap sm:gap-1.5">
          {PERIOD_OPTIONS.map((p) => (
            <button
              key={p.key}
              onClick={() => onPresetChange(p.key)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                preset === p.key ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {isCustom && (
        <div className="mt-3 flex items-center gap-2 border-t border-slate-100 pt-3">
          <input
            type="date"
            value={startDate}
            onChange={(e) => onCustomDateChange(e.target.value, endDate)}
            className="min-w-0 flex-1 rounded-lg border border-slate-200 px-2.5 py-2 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:flex-none"
          />
          <span className="flex-shrink-0 text-xs text-slate-400">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onCustomDateChange(startDate, e.target.value)}
            className="min-w-0 flex-1 rounded-lg border border-slate-200 px-2.5 py-2 text-sm text-slate-700 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 sm:flex-none"
          />
        </div>
      )}
    </div>
  );
}
