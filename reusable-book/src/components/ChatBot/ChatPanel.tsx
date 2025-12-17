import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import styles from './styles.module.css';

interface ChatPanelProps {
  chatBot: any;
  onClose: () => void;
}

export default function ChatPanel({ chatBot, onClose }: ChatPanelProps) {
  return (
    <div className={styles.chatPanel}>
      <div className={styles.chatHeader}>
        <h3>AI Assistant</h3>
        <button onClick={onClose} className={styles.closeButton}>✕</button>
      </div>

      <MessageList messages={chatBot.messages} isLoading={chatBot.isLoading} />

      <MessageInput
        onSend={chatBot.sendMessage}
        disabled={chatBot.isLoading}
      />
    </div>
  );
}
