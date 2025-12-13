import React from 'react';
import Layout from '@theme/Layout';
import Chatbot from '../components/Chatbot';

function ChatPage() {
  return (
    <Layout
      title="Chat with Book"
      description="Ask questions about the book content"
    >
      <main>
        <Chatbot />
      </main>
    </Layout>
  );
}

export default ChatPage;