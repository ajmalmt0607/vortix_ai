import { Sparkles, User } from "lucide-react";

export default function ChatMessage({ role, content, isError }) {
  const isUser = role === "user";
  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-slate-200 text-slate-600" : "bg-indigo-100 text-indigo-600"
        }`}
      >
        {isUser ? <User className="h-3.5 w-3.5" /> : <Sparkles className="h-3.5 w-3.5" />}
      </div>
      <div
        className={`max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed whitespace-pre-line ${
          isUser
            ? "rounded-tr-sm bg-indigo-600 text-white"
            : isError
            ? "rounded-tl-sm bg-rose-50 text-rose-700"
            : "rounded-tl-sm bg-slate-100 text-slate-700"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
