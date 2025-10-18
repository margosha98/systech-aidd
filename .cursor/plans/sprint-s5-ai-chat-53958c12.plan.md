<!-- 53958c12-e9c9-43ee-96a4-6e78f4519021 79999f92-70ea-4c64-9c0f-a86ac6daf26a -->
# Sprint S5: Реализация ИИ-чата

## Обзор

Интеграция AI чата в дашборд с двумя режимами работы:

- **Обычный режим**: общение с LLM-ассистентом
- **Режим администратора**: вопросы по статистике через text-to-SQL

## 1. Backend: API для чата

### 1.1 Модели данных

**Файл**: `backend/api/models.py`

Добавить новые Pydantic модели:

```python
class ChatMode(str, Enum):
    NORMAL = "normal"
    ADMIN = "admin"

class ChatRequest(BaseModel):
    message: str
    mode: ChatMode = ChatMode.NORMAL
    session_id: str  # Для отслеживания истории
    
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    
class ChatResponse(BaseModel):
    message: str
    sql_query: str | None = None  # Для admin режима (debug)
    mode: ChatMode
```

### 1.2 Chat Service

**Файл**: `backend/api/chat_service.py` (новый)

Создать сервис для обработки chat запросов:

```python
class ChatService:
    def __init__(self, llm_client: LLMClient, db_pool):
        self.llm_client = llm_client
        self.db_pool = db_pool
        
    async def process_message(
        self, 
        request: ChatRequest, 
        history: list[Message]
    ) -> ChatResponse:
        if request.mode == ChatMode.NORMAL:
            return await self._process_normal(request, history)
        else:
            return await self._process_admin(request, history)
    
    async def _process_normal(self, request, history):
        # Прямое обращение к LLM
        response = await self.llm_client.get_response(
            messages=history, 
            system_prompt=CHAT_SYSTEM_PROMPT
        )
        return ChatResponse(message=response, mode=ChatMode.NORMAL)
    
    async def _process_admin(self, request, history):
        # 1. Генерация SQL через LLM (text-to-SQL промпт)
        # 2. Выполнение SQL запроса
        # 3. Интерпретация результата через LLM
        pass
```

**Важно**: Переиспользовать `LLMClient` из `src/llm/client.py`, адаптировав под backend структуру

### 1.3 Text-to-SQL промпт

**Файл**: `backend/api/prompts.py` (новый)

```python
TEXT_TO_SQL_PROMPT = """
Ты SQL эксперт. На основе вопроса пользователя создай SQL запрос к базе данных PostgreSQL.

Доступные таблицы:
- messages (id, user_id, chat_id, role, content, created_at, username)

Схема:
{schema}

Вопрос: {question}

Верни только SQL запрос без markdown.
"""

INTERPRET_RESULTS_PROMPT = """
На основе результатов SQL запроса дай понятный ответ на вопрос пользователя.

Вопрос: {question}
SQL запрос: {sql}
Результаты: {results}

Ответь понятным языком, интерпретируя данные.
"""
```

### 1.4 Эндпоинты

**Файл**: `backend/api/server.py`

Добавить новые роуты:

```python
@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    # Загрузить историю по session_id
    # Вызвать ChatService.process_message()
    # Сохранить новое сообщение в историю
    pass

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    # Вернуть историю чата для session_id
    pass
```

## 2. Frontend: UI компонентов чата

### 2.1 Установка зависимостей

**Команда**:

```bash
cd frontend && pnpm add framer-motion
```

**Примечание**: `lucide-react` уже установлен

### 2.2 Типы для Chat API

**Файл**: `frontend/types/api.ts`

Добавить новые типы (синхронизированные с backend):

```typescript
export type ChatMode = 'normal' | 'admin';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  mode: ChatMode;
  session_id: string;
}

export interface ChatResponse {
  message: string;
  sql_query?: string;
  mode: ChatMode;
}
```

### 2.3 Chat API клиент

**Файл**: `frontend/lib/chat-api.ts` (новый)

```typescript
export async function sendChatMessage(
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
}

export async function getChatHistory(
  sessionId: string
): Promise<ChatMessage[]> {
  const response = await fetch(
    `${API_URL}/api/chat/history/${sessionId}`
  );
  
  if (!response.ok) throw new Error('Failed to fetch history');
  return response.json();
}
```

### 2.4 AI Chat компонент

**Файл**: `frontend/components/ui/ai-chat.tsx` (новый)

Адаптировать референс из `21st-ai-chat.md`:

- Добавить props: `mode`, `onModeChange`, `sessionId`
- Интегрировать с `sendChatMessage` API
- Добавить индикатор режима (badge: "Обычный" / "Администратор")
- Добавить toggle для переключения режима
- Для admin режима: опционально показывать SQL запрос
- Обработка ошибок и loading состояний
```tsx
interface AIChatProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  sessionId: string;
  className?: string;
}

export default function AIChat({ mode, onModeChange, sessionId }: AIChatProps) {
  // Логика чата с API интеграцией
}
```


### 2.5 Floating Button

**Файл**: `frontend/components/ui/chat-float-button.tsx` (новый)

Кнопка в правом нижнем углу для открытия чата:

```tsx
'use client';

import { MessageCircle } from 'lucide-react';
import { useState } from 'react';
import AIChat from './ai-chat';

export function ChatFloatButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState<ChatMode>('normal');
  
  return (
    <>
      {/* Floating Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 rounded-full bg-primary p-4 shadow-lg hover:shadow-xl transition-all"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </button>
      
      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-40">
          <AIChat 
            mode={mode} 
            onModeChange={setMode}
            sessionId={generateSessionId()}
          />
        </div>
      )}
    </>
  );
}
```

### 2.6 Интеграция в дашборд

**Файл**: `frontend/app/page.tsx`

Добавить `ChatFloatButton`:

```tsx
import { ChatFloatButton } from '@/components/ui/chat-float-button';

export default async function DashboardPage({ searchParams }: PageProps) {
  // ... существующий код дашборда
  
  return (
    <>
      <div className="container mx-auto p-6 space-y-6">
        {/* Существующие компоненты дашборда */}
      </div>
      
      {/* Floating Chat Button */}
      <ChatFloatButton />
    </>
  );
}
```

## 3. Backend: Text-to-SQL реализация

### 3.1 SQL Generator

**Файл**: `backend/api/sql_generator.py` (новый)

```python
class SQLGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def generate_sql(self, question: str) -> str:
        # Использовать TEXT_TO_SQL_PROMPT
        # Отправить в LLM
        # Вернуть SQL запрос
        pass
    
    async def execute_sql(self, sql: str, db_pool) -> list[dict]:
        # Выполнить SQL через db_pool
        # Вернуть результаты
        pass
    
    async def interpret_results(
        self, 
        question: str, 
        sql: str, 
        results: list[dict]
    ) -> str:
        # Использовать INTERPRET_RESULTS_PROMPT
        # Отправить в LLM для интерпретации
        # Вернуть человекочитаемый ответ
        pass
```

### 3.2 Интеграция в ChatService

**Файл**: `backend/api/chat_service.py`

Реализовать `_process_admin`:

```python
async def _process_admin(self, request, history):
    sql_gen = SQLGenerator(self.llm_client)
    
    # 1. Text-to-SQL
    sql = await sql_gen.generate_sql(request.message)
    
    # 2. Execute SQL
    results = await sql_gen.execute_sql(sql, self.db_pool)
    
    # 3. Interpret
    answer = await sql_gen.interpret_results(
        request.message, sql, results
    )
    
    return ChatResponse(
        message=answer,
        sql_query=sql,  # Для debug
        mode=ChatMode.ADMIN
    )
```

## 4. Интеграция и тестирование

### 4.1 Переиспользование LLM клиента

**Задача**: Создать общий модуль для LLM клиента, доступный и боту и API

Опции:

- Переместить `src/llm/client.py` в общее место
- Создать wrapper в `backend/api/llm_client.py`
- Импортировать напрямую из `src/llm/client.py`

### 4.2 Session Management

**Файл**: `frontend/lib/session.ts` (новый)

```typescript
export function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36)}`;
}

export function getSessionId(): string {
  if (typeof window === 'undefined') return generateSessionId();
  
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}
```

### 4.3 Хранение истории чата

**Опции**:

1. Использовать существующую таблицу `messages` с отдельным chat_id для веб-чата
2. Создать новую таблицу `web_chat_messages`
3. Хранить в памяти (для MVP)

**Рекомендация**: Использовать существующую таблицу с префиксом `web_` для chat_id

## 5. UI/UX улучшения

### 5.1 Адаптивность

- Desktop: Chat размером 360x460px (как в референсе)
- Mobile: Fullscreen overlay
- Анимации открытия/закрытия

### 5.2 Индикация режима

Показывать badge в header чата:

- "💬 Обычный режим" - зеленый badge
- "🔧 Админ режим" - синий badge

### 5.3 SQL Debug Panel (опционально)

Для admin режима показывать collapsible panel с SQL запросом:

```tsx
{mode === 'admin' && sqlQuery && (
  <details className="text-xs bg-muted p-2 rounded">
    <summary>SQL запрос</summary>
    <pre>{sqlQuery}</pre>
  </details>
)}
```

## 6. Документация

### 6.1 Обновить frontend-roadmap.md

- Отметить S5 как "🏗️ В разработке"
- После завершения: статус "✅ Завершен"

### 6.2 API документация

FastAPI автоматически сгенерирует документацию для `/api/chat/*` эндпоинтов

## Структура файлов

```
backend/api/
├── chat_service.py      # NEW: Сервис обработки чата
├── sql_generator.py     # NEW: Text-to-SQL логика
├── prompts.py           # NEW: LLM промпты
├── models.py            # EDIT: Добавить Chat модели
└── server.py            # EDIT: Добавить /api/chat/* роуты

frontend/
├── components/
│   └── ui/
│       ├── ai-chat.tsx           # NEW: Компонент чата
│       └── chat-float-button.tsx # NEW: Floating button
├── lib/
│   ├── chat-api.ts      # NEW: Chat API клиент
│   └── session.ts       # NEW: Session management
├── types/
│   └── api.ts           # EDIT: Добавить Chat типы
└── app/
    └── page.tsx         # EDIT: Добавить ChatFloatButton
```

## Зависимости между задачами

1. Backend модели → Backend API
2. Backend API → Frontend типы
3. Frontend типы → Frontend компоненты
4. Frontend компоненты → Интеграция в дашборд
5. LLM интеграция → Text-to-SQL
6. Text-to-SQL → Admin режим

### To-dos

- [ ] Создать Pydantic модели для Chat API в backend/api/models.py
- [ ] Создать промпты для text-to-SQL и интерпретации в backend/api/prompts.py
- [ ] Реализовать SQLGenerator для text-to-SQL в backend/api/sql_generator.py
- [ ] Создать ChatService для обработки сообщений в backend/api/chat_service.py
- [ ] Добавить эндпоинты /api/chat/* в backend/api/server.py
- [ ] Добавить типы для Chat API в frontend/types/api.ts
- [ ] Создать Chat API клиент в frontend/lib/chat-api.ts
- [ ] Реализовать session management в frontend/lib/session.ts
- [ ] Установить framer-motion через pnpm
- [ ] Создать компонент AIChat в frontend/components/ui/ai-chat.tsx
- [ ] Создать ChatFloatButton в frontend/components/ui/chat-float-button.tsx
- [ ] Интегрировать ChatFloatButton в app/page.tsx
- [ ] Протестировать оба режима чата (normal и admin) и интеграцию с дашбордом