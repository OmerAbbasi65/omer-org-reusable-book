import React, { useState, useEffect, useRef } from "react";
import styles from "./ChatWidget.module.css"; // optional styling

// Backend URL - uses HF Space in production, localhost for development
const BACKEND_URL = process.env.NODE_ENV === 'production'
  ? 'https://joseph8071-robotics-rag-backend.hf.space'
  : 'http://localhost:8000';

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "bot", text: "👋 Welcome! I'm here to help you with any questions about this book." }
  ]);
  const [input, setInput] = useState("");
  const [selection, setSelection] = useState({ text: "", position: null });
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const drawerRef = useRef(null);

  // Generate session ID on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedSessionId = localStorage.getItem('chatSessionId');
      if (storedSessionId) {
        setSessionId(storedSessionId);
      } else {
        const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        localStorage.setItem('chatSessionId', newSessionId);
      }
    }
  }, []);

  useEffect(() => {
    const handleMouseUp = () => {
      const selectedText = window.getSelection().toString();
      if (selectedText) {
        const range = window.getSelection().getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelection({
          text: selectedText,
          position: { top: rect.bottom + window.scrollY, left: rect.left + window.scrollX },
        });
      } else {
        setSelection({ text: "", position: null });
      }
    };

    document.addEventListener("mouseup", handleMouseUp);
    return () => document.removeEventListener("mouseup", handleMouseUp);
  }, []);

  const handleSelectionAsk = () => {
    setOpen(true);
    setInput(`What about "${selection.text}"?`);
    setSelection({ text: "", position: null });
  };

  const sendMessage = async (messageText) => {
    const text = messageText || input;
    if (!text.trim()) return;

    const userMsg = { from: "user", text: text.trim() };
    setMessages((old) => [...old, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const requestBody = {
        message: userMsg.text,
        session_id: sessionId,
        selected_text: selection.text || null
      };

      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = {
        from: "bot",
        text: data.response,
        sources: data.sources,
        confidence: data.confidence
      };
      setMessages((old) => [...old, botMessage]);

      // Update session ID if server provided new one
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        if (typeof window !== 'undefined') {
          localStorage.setItem('chatSessionId', data.session_id);
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = error.message.includes('Failed to fetch') || error.message.includes('NetworkError')
        ? '❌ Cannot connect to chatbot server.\n\n🔧 To fix:\n1. Open a terminal\n2. Run: cd backend\n3. Run: uvicorn app.main:app --reload\n4. Make sure it says "API is ready"\n5. Try your question again!'
        : `❌ Error: ${error.message}\n\nPlease check the backend server is running.`;

      setMessages((old) => [...old, { from: "bot", text: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  // Click outside to close
  useEffect(() => {
    if (!open) return;

    const handleClickOutside = (event) => {
      if (drawerRef.current && !drawerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open]);

  const closeChat = () => {
    setOpen(false);
  };

  return (
    <>
      {selection.position && (
        <button
          className={styles.selectionFab}
          style={{ top: selection.position.top, left: selection.position.left }}
          onClick={handleSelectionAsk}
        >
          💡 Ask about this?
        </button>
      )}

      {/* Floating button - only show when chat is closed */}
      {!open && (
        <button className={styles.fab} onClick={() => setOpen(true)} title="Open Chat Assistant">
          💬
        </button>
      )}

      {/* Drawer / Modal */}
      {open && (
        <div className={styles.overlay}>
          <div className={styles.drawer} ref={drawerRef}>
            <div className={styles.header}>
              <span>🤖 AI Tutor</span>
              <button onClick={closeChat} className={styles.closeButton} title="Close chat (or click outside)">
                ✕
              </button>
            </div>

            <div className={styles.messages}>
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={m.from === "user" ? styles.userMsg : styles.botMsg}
                >
                  <div className={styles.messageText}>{m.text}</div>
                  {m.sources && m.sources.length > 0 && (
                    <div className={styles.sources}>
                      <details>
                        <summary>📚 Sources ({m.sources.length})</summary>
                        {m.sources.map((source, idx) => (
                          <div key={idx} className={styles.sourceItem}>
                            {source.title}
                          </div>
                        ))}
                      </details>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className={styles.botMsg}>
                  <div className={styles.loadingDots}>
                    <span>.</span><span>.</span><span>.</span>
                  </div>
                </div>
              )}
            </div>

            <div className={styles.inputRow}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !loading) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask about the book..."
                disabled={loading}
              />
              <button onClick={() => sendMessage()} disabled={loading || !input.trim()}>
                {loading ? '...' : '📤'}
              </button>
            </div>

            <div className={styles.footer}>
              <small>💡 Tip: Select text on the page to ask specific questions!</small>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
