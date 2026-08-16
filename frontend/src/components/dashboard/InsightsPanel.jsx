import { AlertTriangle, Sparkles, TrendingUp, Lightbulb } from "lucide-react";
import { useAIChat } from "../../context/AIChatContext";
import EmptyState from "../common/EmptyState";

const STYLE = {
  POSITIVE: { badge: "bg-emerald-50 text-emerald-700", icon: TrendingUp },
  WARNING: { badge: "bg-rose-50 text-rose-700", icon: AlertTriangle },
  OPPORTUNITY: { badge: "bg-amber-50 text-amber-700", icon: Lightbulb },
};

export default function InsightsPanel({ insights }) {
  const { openWithQuestion } = useAIChat();

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-4">
        <Sparkles className="h-4 w-4 text-indigo-500" />
        <h3 className="text-sm font-semibold text-slate-900">AI Business Insights</h3>
      </div>
      <div className="p-5">
        {!insights || insights.length === 0 ? (
          <EmptyState
            title="No insights yet"
            message="Insights will appear here once there's enough data to analyze."
          />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {insights.map((insight, idx) => {
              const style = STYLE[insight.type] || STYLE.OPPORTUNITY;
              const Icon = style.icon;
              return (
                <div key={idx} className="rounded-lg border border-slate-100 p-4">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${style.badge}`}
                  >
                    <Icon className="h-3 w-3" />
                    {insight.severity}
                  </span>
                  <p className="mt-2 text-sm font-medium text-slate-800">{insight.title}</p>
                  <p className="mt-1 text-xs text-slate-500">{insight.description}</p>
                  <button
                    onClick={() => openWithQuestion(insight.title)}
                    className="mt-3 text-xs font-medium text-indigo-600 hover:text-indigo-700"
                  >
                    Ask AI →
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
