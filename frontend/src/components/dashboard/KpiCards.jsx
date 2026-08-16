import { DollarSign, ShoppingBag, Wallet, TrendingUp, TrendingDown } from "lucide-react";
import { formatMoney, formatNumber, formatPercent } from "../../utils/format";

function GrowthBadge({ value }) {
  if (value === null || value === undefined) return null;
  const positive = value >= 0;
  const Icon = positive ? TrendingUp : TrendingDown;
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-medium ${
        positive ? "text-emerald-600" : "text-rose-600"
      }`}
    >
      <Icon className="h-3.5 w-3.5 flex-shrink-0" />
      {formatPercent(value)}
    </span>
  );
}

export default function KpiCards({ summary, comparison }) {
  const revenueGrowth = comparison?.revenue_growth;
  const GrowthIcon = revenueGrowth >= 0 ? TrendingUp : TrendingDown;

  const cards = [
    {
      key: "revenue",
      label: "Revenue",
      value: formatMoney(summary.revenue),
      icon: DollarSign,
      growth: comparison?.revenue_growth,
    },
    {
      key: "orders",
      label: "Orders",
      value: formatNumber(summary.orders),
      icon: ShoppingBag,
      growth: comparison?.orders_growth,
    },
    {
      key: "aov",
      label: "Average Order",
      value: formatMoney(summary.average_order_value),
      icon: Wallet,
      growth: comparison?.aov_growth,
    },
    {
      key: "growth",
      label: "Growth",
      value: formatPercent(revenueGrowth),
      icon: GrowthIcon,
      caption: "vs previous period",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.key}
          className="min-w-0 rounded-xl border border-slate-200 bg-white p-3.5 shadow-sm sm:p-5"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-[10px] font-medium uppercase tracking-wide text-slate-400 sm:text-xs">
              {card.label}
            </span>
            <card.icon className="h-4 w-4 flex-shrink-0 text-indigo-500" />
          </div>
          <p className="mt-1.5 truncate text-lg font-semibold text-slate-900 sm:mt-2 sm:text-2xl">
            {card.value}
          </p>
          {card.caption ? (
            <p className="mt-1.5 text-[11px] text-slate-400 sm:mt-2 sm:text-xs">{card.caption}</p>
          ) : (
            <div className="mt-1.5 flex items-center gap-1.5 sm:mt-2">
              <GrowthBadge value={card.growth} />
              <span className="hidden text-xs text-slate-400 xs:inline sm:inline">vs previous</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
