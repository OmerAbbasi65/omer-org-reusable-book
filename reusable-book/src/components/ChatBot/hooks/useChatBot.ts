import { useState, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function useChatBot() {
  const { siteConfig } = useDocusaurusContext();
  const backendUrl = (siteConfig.customFields?.backendUrl as string) || 'https://joseph8071-robotics-rag-backend.hf.space';
  const API_URL = `${backendUrl}/api`;

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);

  const createSession = useCallback(() => {
    // Generate session ID on client side
    const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    return newSessionId;
  }, []);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    let currentSessionId = sessionId;
    if (!currentSessionId) {
      currentSessionId = createSession();
    }

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: currentSessionId,
          selected_text: selectedText,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
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
  }, [sessionId, selectedText, createSession, API_URL]);

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
