import { createContext, useCallback, useContext, useState } from "react";

const AIChatContext = createContext(null);

export function AIChatProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState(null);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const openWithQuestion = useCallback((question) => {
    setPendingQuestion(question);
    setIsOpen(true);
  }, []);
  const clearPendingQuestion = useCallback(() => setPendingQuestion(null), []);

  return (
    <AIChatContext.Provider
      value={{ isOpen, open, close, openWithQuestion, pendingQuestion, clearPendingQuestion }}
    >
      {children}
    </AIChatContext.Provider>
  );
}

export function useAIChat() {
  const ctx = useContext(AIChatContext);
  if (!ctx) throw new Error("useAIChat must be used within AIChatProvider");
  return ctx;
}
