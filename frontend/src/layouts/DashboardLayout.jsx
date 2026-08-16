import { Outlet } from "react-router-dom";
import Sidebar from "../components/common/Sidebar";
import Topbar from "../components/common/Topbar";
import AICopilot from "../components/ai/AICopilot";

export default function DashboardLayout() {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-900">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-4 pb-[calc(4rem+env(safe-area-inset-bottom)+1rem)] sm:p-6 lg:p-8 lg:pb-8">
          <Outlet />
        </main>
      </div>
      <AICopilot />
    </div>
  );
}
