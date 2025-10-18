# AI Chat Component Reference (21st.dev)

Референс компонента чата от 21st.dev для интеграции в проект.

## Описание

Готовый компонент React-чата с анимациями и современным UI для реализации административного чата со статистикой.

## Технические требования

Проект должен поддерживать:
- shadcn project structure
- Tailwind CSS
- TypeScript

Если проект не поддерживает эти технологии, необходимо настроить через shadcn CLI.

## Структура компонентов

### Основной компонент: ai-chat.tsx

Расположение: `/components/ui/ai-chat.tsx`

```tsx
"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AIChatCard({ className }: { className?: string }) {
  const [messages, setMessages] = useState<{ sender: "ai" | "user"; text: string }[]>([
    { sender: "ai", text: "👋 Hello! I'm your AI assistant." },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      setMessages((prev) => [...prev, { sender: "ai", text: "🤖 This is a sample AI response." }]);
      setIsTyping(false);
    }, 1200);
  };

  return (
    <div className={cn("relative w-[360px] h-[460px] rounded-2xl overflow-hidden p-[2px]", className)}>
      {/* Animated Outer Border */}
      <motion.div
        className="absolute inset-0 rounded-2xl border-2 border-white/20"
        animate={{ rotate: [0, 360] }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
      />

      {/* Inner Card */}
      <div className="relative flex flex-col w-full h-full rounded-xl border border-white/10 overflow-hidden bg-black/90 backdrop-blur-xl">
        {/* Inner Animated Background */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-gray-800 via-black to-gray-900"
          animate={{ backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"] }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          style={{ backgroundSize: "200% 200%" }}
        />

        {/* Floating Particles */}
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

        {/* Header */}
        <div className="px-4 py-3 border-b border-white/10 relative z-10">
          <h2 className="text-lg font-semibold text-white">🤖 AI Assistant</h2>
        </div>

        {/* Messages */}
        <div className="flex-1 px-4 py-3 overflow-y-auto space-y-3 text-sm flex flex-col relative z-10">
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className={cn(
                "px-3 py-2 rounded-xl max-w-[80%] shadow-md backdrop-blur-md",
                msg.sender === "ai"
                  ? "bg-white/10 text-white self-start"
                  : "bg-white/30 text-black font-semibold self-end"
              )}
            >
              {msg.text}
            </motion.div>
          ))}

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
        </div>

        {/* Input */}
        <div className="flex items-center gap-2 p-3 border-t border-white/10 relative z-10">
          <input
            className="flex-1 px-3 py-2 text-sm bg-black/50 rounded-lg border border-white/10 text-white focus:outline-none focus:ring-1 focus:ring-white/50"
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
          >
            <Send className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Demo компонент: demo.tsx

```tsx
import AIChatCard from "@/components/ui/ai-chat";

export default function DemoOne() {
  return <AIChatCard />;
}
```

## Установка зависимостей

```bash
npm install lucide-react framer-motion
# или
pnpm add lucide-react framer-motion
```

## Рекомендации по интеграции

### 1. Анализ структуры компонента
- Определить все зависимости (framer-motion, lucide-react)
- Проверить аргументы и state компонента
- Выявить необходимые context providers и hooks

### 2. Вопросы перед интеграцией
- Какие данные/props будут переданы компоненту?
- Требования к state management?
- Необходимые assets (изображения, иконки)?
- Ожидаемое responsive поведение?
- Оптимальное место использования в приложении?

### 3. Шаги интеграции
0. Скопировать код в правильные директории (`/components/ui`)
1. Установить внешние зависимости
2. Заполнить image assets через Unsplash (если требуется)
3. Использовать lucide-react для иконок/логотипов

## Примечания

- Компонент использует Tailwind CSS для стилизации
- Анимации реализованы через framer-motion
- Иконки из библиотеки lucide-react
- Требуется утилита `cn` из `@/lib/utils`
- Компонент адаптирован под dark theme

