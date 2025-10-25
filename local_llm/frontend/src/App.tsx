import { FormEvent, KeyboardEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react';

type Role = 'user' | 'assistant';

interface Message {
  id: string;
  role: Role;
  content: string;
}

const createId = () => (typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : Math.random().toString(36).slice(2));

const assistantPlaceholder = '...';

const App = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const element = chatContainerRef.current;
    if (element) {
      element.scrollTop = element.scrollHeight;
    }
  }, [messages]);

  const handleStream = useCallback(
    async (prompt: string) => {
      const userMessage: Message = { id: createId(), role: 'user', content: prompt };
      const assistantMessage: Message = { id: createId(), role: 'assistant', content: assistantPlaceholder };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsStreaming(true);

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: sessionId,
            message: prompt
          })
        });

        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || 'チャットの送信に失敗しました。');
        }

        const headerSessionId = response.headers.get('x-session-id');
        if (headerSessionId) {
          setSessionId(headerSessionId);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('レスポンスのストリームを取得できませんでした。');
        }

        const decoder = new TextDecoder();
        let accumulated = '';

        // Update the assistant message incrementally as chunks arrive.
        const pushUpdate = (content: string) =>
          setMessages((prev) =>
            prev.map((message) =>
              message.id === assistantMessage.id ? { ...message, content } : message
            )
          );

        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            break;
          }
          accumulated += decoder.decode(value, { stream: true });
          pushUpdate(accumulated);
        }

        accumulated += decoder.decode();
        pushUpdate(accumulated.trim() || '');
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        setMessages((prev) =>
          prev.map((item) =>
            item.id === assistantMessage.id
              ? { ...item, content: `[エラー] ${message}` }
              : item
          )
        );
      } finally {
        setIsStreaming(false);
      }
    },
    [sessionId]
  );

  const submit = useCallback(
    async (event?: FormEvent<HTMLFormElement>) => {
      if (event) {
        event.preventDefault();
      }

      if (isStreaming) {
        return;
      }

      const prompt = input.trim();
      if (!prompt) {
        return;
      }

      setInput('');
      await handleStream(prompt);
    },
    [handleStream, input, isStreaming]
  );

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        void submit();
      }
    },
    [submit]
  );

  const statusMessage = useMemo(() => {
    if (isStreaming) {
      return '応答を生成中...';
    }
    if (!sessionId) {
      return '新しいセッションを開始しました。';
    }
    return `セッションID: ${sessionId}`;
  }, [isStreaming, sessionId]);

  return (
    <div className="app">
      <header className="app__header">
        <h1>ローカルLLMチャット</h1>
        <span className="app__status" aria-live="polite">
          {statusMessage}
        </span>
      </header>

      <main className="chat" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div className="chat__placeholder">
            <p>モデルに質問してみましょう。Shift+Enterで改行します。</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`chat__message chat__message--${message.role}`}>
              <div className="chat__bubble">
                {message.content || (message.role === 'assistant' ? assistantPlaceholder : '')}
              </div>
            </div>
          ))
        )}
      </main>

      <form className="composer" onSubmit={submit}>
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="メッセージを入力..."
          disabled={isStreaming}
          rows={3}
        />
        <button type="submit" disabled={isStreaming || input.trim().length === 0}>
          {isStreaming ? '送信中...' : '送信'}
        </button>
      </form>
    </div>
  );
};

export default App;
