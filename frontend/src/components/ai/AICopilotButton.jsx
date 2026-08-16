import { Sparkles } from "lucide-react";
import { useAIChat } from "../../context/AIChatContext";

export default function AICopilotButton() {
  const { open, isOpen } = useAIChat();
  if (isOpen) return null;

  return (
    <button
      onClick={open}
      className="fixed right-4 z-40 flex h-11 w-11 items-center justify-center gap-2 rounded-full bg-indigo-600 text-white shadow-lg shadow-indigo-600/25 transition-colors hover:bg-indigo-700 xs:w-auto xs:justify-start xs:px-4 bottom-[calc(4rem+env(safe-area-inset-bottom)+0.75rem)] lg:bottom-5 lg:right-5"
    >
      <Sparkles className="h-4 w-4 flex-shrink-0" />
      <span className="hidden text-sm font-semibold xs:inline">Ask AI</span>
    </button>
  );
}
