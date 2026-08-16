import { Sparkles } from "lucide-react";

export default function Topbar() {
  return (
    <header className="flex h-16 flex-shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
      <div className="flex items-center gap-2 lg:hidden">
        <Sparkles className="h-4 w-4 flex-shrink-0 text-indigo-600" />
        <div className="leading-tight">
          <p className="text-sm font-semibold text-slate-900">VORTIX</p>
          <p className="text-[10px] text-slate-400">Restaurant Intelligence</p>
        </div>
      </div>
      <div className="hidden text-sm font-medium text-slate-500 lg:block">AI Restaurant Intelligence</div>
      <div className="text-xs font-medium text-slate-400 sm:text-sm">UAE Restaurant</div>
    </header>
  );
}
