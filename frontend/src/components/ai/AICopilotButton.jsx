import { Sparkles } from "lucide-react";
import { useAIChat } from "../../context/AIChatContext";

export default function AICopilotButton() {
  const { open, isOpen } = useAIChat();
  if (isOpen) return null;

  return (
    <button
      onClick={open}
      className="fixed bottom-20 right-5 z-40 inline-flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition-colors hover:bg-indigo-700 lg:bottom-5"
    >
      <Sparkles className="h-4 w-4" />
      Ask VORTIX AI
    </button>
  );
}
