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
      <Icon className="h-3.5 w-3.5" />
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
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div key={card.key} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">{card.label}</span>
            <card.icon className="h-4 w-4 text-indigo-500" />
          </div>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{card.value}</p>
          {card.caption ? (
            <p className="mt-2 text-xs text-slate-400">{card.caption}</p>
          ) : (
            <div className="mt-2 flex items-center gap-1.5">
              <GrowthBadge value={card.growth} />
              <span className="text-xs text-slate-400">vs previous period</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
