import { Sparkles, User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkBreaks from "remark-breaks";

const markdownComponents = {
  p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
  strong: ({ node, ...props }) => <strong className="font-semibold text-slate-900" {...props} />,
  ul: ({ node, ...props }) => (
    <ul className="mb-2 ml-4 list-disc space-y-0.5 marker:text-slate-400 last:mb-0" {...props} />
  ),
  ol: ({ node, ...props }) => (
    <ol className="mb-2 ml-4 list-decimal space-y-0.5 marker:text-slate-400 last:mb-0" {...props} />
  ),
  li: ({ node, ...props }) => <li className="pl-0.5" {...props} />,
  a: ({ node, ...props }) => <a className="underline underline-offset-2" {...props} />,
};

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
        className={`max-w-[82%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
          isUser
            ? "rounded-tr-sm bg-indigo-600 text-white"
            : isError
            ? "rounded-tl-sm bg-rose-50 text-rose-700"
            : "rounded-tl-sm bg-slate-100 text-slate-700"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-line">{content}</p>
        ) : (
          <ReactMarkdown remarkPlugins={[remarkBreaks]} components={markdownComponents}>
            {content}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}
