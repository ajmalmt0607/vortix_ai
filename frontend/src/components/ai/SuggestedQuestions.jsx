const QUESTIONS = [
  { emoji: "💰", text: "What were today's sales?" },
  { emoji: "📈", text: "What were sales last week?" },
  { emoji: "🏆", text: "What is our best-selling food?" },
  { emoji: "📍", text: "Which branch is performing best?" },
  { emoji: "🤝", text: "What do customers order with Chicken Burger?" },
  { emoji: "⏰", text: "When is our busiest time?" },
  { emoji: "💡", text: "Give me a quick summary of my restaurant." },
];

export default function SuggestedQuestions({ onSelect }) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Popular questions</p>
      <div className="flex flex-col gap-1.5">
        {QUESTIONS.map((q) => (
          <button
            key={q.text}
            onClick={() => onSelect(q.text)}
            className="flex items-center gap-2.5 rounded-xl border border-slate-200 px-3.5 py-2.5 text-left text-sm text-slate-700 transition-colors hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
          >
            <span className="flex-shrink-0 text-base leading-none">{q.emoji}</span>
            <span>{q.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
