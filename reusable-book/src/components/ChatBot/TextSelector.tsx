import React from 'react';
import styles from './styles.module.css';

interface TextSelectorProps {
  position: { x: number; y: number };
  onAsk: () => void;
  onDismiss: () => void;
}

export default function TextSelector({ position, onAsk, onDismiss }: TextSelectorProps) {
  const topPosition = position.y + 10;
  return (
    <div
      className={styles.textSelector}
      style={{
        left: position.x + 'px',
        top: topPosition + 'px',
      }}
    >
      <button onClick={onAsk}>Ask about this</button>
      <button onClick={onDismiss} className={styles.dismissButton}>✕</button>
    </div>
  );
}
