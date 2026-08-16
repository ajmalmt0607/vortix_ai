const QUESTIONS = [
  "What were today's sales?",
  "What were sales last week?",
  "What is our best-selling food?",
  "Which branch is performing best?",
  "What do customers order with Chicken Burger?",
  "When is our busiest time?",
  "Give me a quick summary of my restaurant.",
];

export default function SuggestedQuestions({ onSelect }) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Suggested questions</p>
      <div className="flex flex-col gap-1.5">
        {QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-left text-sm text-slate-600 transition-colors hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
