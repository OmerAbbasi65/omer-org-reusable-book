import React, { useEffect, useRef } from 'react';
import styles from './styles.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatMessages}>
      {messages.length === 0 && (
        <div className={styles.welcomeMessage}>
          <p>👋 Hello! I am your AI assistant for the Physical AI and Humanoid Robotics book.</p>
          <p>Ask me anything about the book content!</p>
        </div>
      )}

      {messages.map((message, index) => (
        <div
          key={index}
          className={`${styles.message} ${styles[message.role]}`}
        >
          <div className={styles.messageContent}>{message.content}</div>
        </div>
      ))}

      {isLoading && (
        <div className={`${styles.message} ${styles.assistant}`}>
          <div className={styles.messageContent}>
            <span className={styles.loadingDots}>Thinking</span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
