"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Settings, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ChatMode } from "@/types/api";
import { sendChatMessage } from "@/lib/chat-api";

interface Message {
  sender: "ai" | "user";
  text: string;
  sqlQuery?: string;
}

interface AIChatProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  sessionId: string;
  className?: string;
  onClose?: () => void;
}

export default function AIChat({ 
  mode, 
  onModeChange, 
  sessionId, 
  className,
  onClose 
}: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { 
      sender: "ai", 
      text: mode === 'admin' 
        ? "👋 Здравствуйте! Я помогу вам с вопросами по статистике диалогов." 
        : "👋 Привет! Я ваш AI-ассистент." 
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Обновляем приветствие при смене режима
  useEffect(() => {
    setMessages([
      { 
        sender: "ai", 
        text: mode === 'admin' 
          ? "👋 Здравствуйте! Я помогу вам с вопросами по статистике диалогов." 
          : "👋 Привет! Я ваш AI-ассистент." 
      },
    ]);
  }, [mode]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");
    setError(null);
    
    // Добавляем сообщение пользователя
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setIsTyping(true);

    try {
      // Отправляем сообщение на сервер
      const response = await sendChatMessage({
        message: userMessage,
        mode: mode,
        session_id: sessionId,
      });

      // Добавляем ответ AI
      setMessages((prev) => [
        ...prev, 
        { 
          sender: "ai", 
          text: response.message,
          sqlQuery: response.sql_query 
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      setError('Произошла ошибка при отправке сообщения');
      setMessages((prev) => [
        ...prev, 
        { 
          sender: "ai", 
          text: "Извините, произошла ошибка. Попробуйте еще раз." 
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={cn("relative w-[360px] h-full max-h-full rounded-2xl", className)}>
      {/* Animated Outer Border */}
      <motion.div
        className="absolute inset-0 rounded-2xl border-2 border-white/20 pointer-events-none"
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      />

      {/* Inner Card */}
      <div className="relative flex flex-col w-full h-full rounded-xl border border-white/10 bg-black/90 backdrop-blur-xl shadow-2xl">
        {/* Inner Animated Background */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-gray-800 via-black to-gray-900 rounded-xl overflow-hidden"
          animate={{ backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          style={{ backgroundSize: "200% 200%" }}
        />

        {/* Floating Particles Container */}
        <div className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
          {Array.from({ length: 20 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 rounded-full bg-white/10"
              animate={{
                y: ["0%", "-140%"],
                x: [Math.random() * 200 - 100, Math.random() * 200 - 100],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: 5 + Math.random() * 3,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "easeInOut",
              }}
              style={{ left: `${Math.random() * 100}%`, bottom: "-10%" }}
            />
          ))}
        </div>

        {/* Header */}
        <div className="px-4 py-3 border-b border-white/10 relative z-10 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-white whitespace-nowrap">🤖 AI Ассистент</h2>
            {/* Mode Badge */}
            <span 
              className={cn(
                "text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap",
                mode === 'admin' 
                  ? "bg-blue-500/20 text-blue-300" 
                  : "bg-green-500/20 text-green-300"
              )}
            >
              {mode === 'admin' ? '🔧 Админ' : '💬 Обычный'}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => onModeChange(mode === 'normal' ? 'admin' : 'normal')}
              className="p-2 rounded-lg bg-white/40 hover:bg-white/60 border-2 border-white/60 hover:border-white transition-all shadow-lg hover:shadow-xl shrink-0"
              title="Переключить режим"
            >
              <Settings className="w-5 h-5 text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]" />
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-white/40 hover:bg-white/60 border-2 border-white/60 hover:border-white transition-all shadow-lg hover:shadow-xl shrink-0"
                title="Закрыть"
              >
                <X className="w-5 h-5 text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]" />
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 min-h-0 px-4 py-3 overflow-y-auto space-y-3 text-sm flex flex-col relative z-10">
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.4 }}
                className="flex flex-col gap-1"
              >
                <div
                  className={cn(
                    "px-3 py-2 rounded-xl max-w-[80%] shadow-md backdrop-blur-md",
                    msg.sender === "ai"
                      ? "bg-white/10 text-white self-start"
                      : "bg-white/30 text-black font-semibold self-end"
                  )}
                >
                  {msg.text}
                </div>
                
                {/* SQL Query Debug Panel */}
                {msg.sqlQuery && mode === 'admin' && (
                  <details className="text-xs bg-white/5 p-2 rounded max-w-[80%] self-start">
                    <summary className="text-white/70 cursor-pointer hover:text-white">
                      SQL запрос
                    </summary>
                    <pre className="text-white/90 mt-1 overflow-x-auto whitespace-pre-wrap">
                      {msg.sqlQuery}
                    </pre>
                  </details>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* AI Typing Indicator */}
          {isTyping && (
            <motion.div
              className="flex items-center gap-1 px-3 py-2 rounded-xl max-w-[30%] bg-white/10 self-start"
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 1, 0.6, 1] }}
              transition={{ repeat: Infinity, duration: 1.2 }}
            >
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-200"></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-400"></span>
            </motion.div>
          )}

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="px-3 py-2 rounded-xl bg-red-500/20 text-red-300 text-xs self-center"
            >
              {error}
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex items-center gap-2 p-3 border-t border-white/10 relative z-10 shrink-0">
          <input
            className="flex-1 px-3 py-2 text-sm bg-black/50 rounded-lg border border-white/10 text-white placeholder:text-white/50 focus:outline-none focus:ring-1 focus:ring-white/50"
            placeholder="Напишите сообщение..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={isTyping}
          />
          <button
            onClick={handleSend}
            disabled={isTyping || !input.trim()}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}

