import { useEffect, useRef, useState } from "react";
import { Sparkles, X, Send, Loader2 } from "lucide-react";
import { useAIChat } from "../../context/AIChatContext";
import { sendAIMessage } from "../../services/api";
import { getErrorMessage } from "../../utils/errors";
import ChatMessage from "./ChatMessage";
import SuggestedQuestions from "./SuggestedQuestions";

export default function AICopilotDrawer() {
  const { isOpen, close, pendingQuestion, clearPendingQuestion } = useAIChat();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  useEffect(() => {
    if (isOpen && pendingQuestion) {
      const question = pendingQuestion;
      clearPendingQuestion();
      handleSend(question);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, pendingQuestion]);

  async function handleSend(text) {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const result = await sendAIMessage(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer || "I couldn't find an answer to that." },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: getErrorMessage(err, "I couldn't answer that right now. Please try again."),
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-end sm:p-5">
      <div className="absolute inset-0 bg-slate-900/20 sm:hidden" onClick={close} />
      <div className="relative flex h-full w-full flex-col bg-white shadow-2xl sm:h-[600px] sm:max-h-[85vh] sm:w-[380px] sm:rounded-2xl sm:border sm:border-slate-200">
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3.5">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-600 text-white">
              <Sparkles className="h-3.5 w-3.5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">VORTIX AI</p>
              <p className="text-[11px] text-slate-400">Restaurant intelligence assistant</p>
            </div>
          </div>
          <button
            onClick={close}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
          {messages.length === 0 ? (
            <>
              <p className="text-sm text-slate-500">
                Ask anything about your restaurant's sales, orders, products or branches.
              </p>
              <SuggestedQuestions onSelect={(q) => handleSend(q)} />
            </>
          ) : (
            messages.map((m, idx) => <ChatMessage key={idx} {...m} />)
          )}
          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              VORTIX AI is thinking...
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 border-t border-slate-100 px-3 py-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask VORTIX..."
            className="flex-1 rounded-full border border-slate-200 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-indigo-600 text-white disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
