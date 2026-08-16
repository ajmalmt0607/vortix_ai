import { Inbox } from "lucide-react";

export default function EmptyState({ title = "Nothing here yet", message, icon: Icon = Inbox }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center text-slate-400">
      <Icon className="h-8 w-8" />
      <p className="text-sm font-medium text-slate-500">{title}</p>
      {message && <p className="max-w-xs text-xs text-slate-400">{message}</p>}
    </div>
  );
}
