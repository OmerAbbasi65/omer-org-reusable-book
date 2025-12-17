import React, { useState } from 'react';
import ChatButton from './ChatButton';
import ChatPanel from './ChatPanel';
import useChatBot from './hooks/useChatBot';
import useTextSelection from './hooks/useTextSelection';
import TextSelector from './TextSelector';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const { selectedText, selectionPosition, clearSelection } = useTextSelection();
  const chatBot = useChatBot();

  const handleOpenWithSelection = () => {
    if (selectedText) {
      chatBot.setSelectedText(selectedText);
      clearSelection();
    }
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    chatBot.resetSession();
  };

  return (
    <>
      {selectedText && selectionPosition && !isOpen && (
        <TextSelector
          position={selectionPosition}
          onAsk={handleOpenWithSelection}
          onDismiss={clearSelection}
        />
      )}

      <ChatButton onClick={() => setIsOpen(!isOpen)} isOpen={isOpen} />

      {isOpen && <ChatPanel chatBot={chatBot} onClose={handleClose} />}
    </>
  );
}
