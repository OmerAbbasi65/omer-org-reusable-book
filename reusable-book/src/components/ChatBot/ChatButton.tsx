import React from 'react';
import styles from './styles.module.css';

interface ChatButtonProps {
  onClick: () => void;
  isOpen: boolean;
}

export default function ChatButton({ onClick, isOpen }: ChatButtonProps) {
  return (
    <button
      className={styles.chatButton}
      onClick={onClick}
      aria-label={isOpen ? "Close chatbot" : "Open chatbot"}
    >
      {isOpen ? '✕' : '💬'}
    </button>
  );
}
