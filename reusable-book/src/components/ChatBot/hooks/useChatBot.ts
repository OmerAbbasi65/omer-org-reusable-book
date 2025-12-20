import { useState, useCallback } from 'react';

// API URL - uses environment variable or defaults to Hugging Face Space
const API_URL = process.env.BACKEND_URL
  ? `${process.env.BACKEND_URL}/api`
  : process.env.NODE_ENV === 'production'
    ? 'https://joseph8071-robotics-rag-backend.hf.space/api'
    : 'http://localhost:8000/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function useChatBot() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);

  const createSession = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/chat/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metadata: {} }),
      });
      const data = await response.json();
      setSessionId(data.session_id);
      return data.session_id;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = await createSession();
      if (!currentSessionId) return;
    }

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/chat/sessions/${currentSessionId}/messages`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            selected_text: selectedText,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.assistant_message.content,
        timestamp: new Date(data.assistant_message.timestamp),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setSelectedText(null);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, selectedText, createSession]);

  const resetSession = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setSelectedText(null);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    resetSession,
    setSelectedText,
  };
}
