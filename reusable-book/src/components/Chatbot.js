import React, { useState, useEffect, useRef } from 'react';
import styles from './Chatbot.module.css';

const BACKEND_URL = (typeof process !== 'undefined' && process.env?.REACT_APP_BACKEND_URL) || 'http://localhost:8000';

const Chatbot = ({ selectedText = null, chapterId = null }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

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

    // Show selected text notification
    useEffect(() => {
        if (selectedText) {
            const notification = {
                text: `📝 Selected text: "${selectedText.substring(0, 100)}${selectedText.length > 100 ? '...' : ''}"`,
                sender: 'system'
            };
            setMessages((prev) => [...prev, notification]);
        }
    }, [selectedText]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (inputMessage.trim() === '') return;

        const userMessage = {
            text: inputMessage,
            sender: 'user',
            timestamp: new Date().toISOString()
        };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setInputMessage('');
        setLoading(true);

        try {
            const requestBody = {
                message: inputMessage,
                session_id: sessionId,
                selected_text: selectedText,
                chapter_id: chapterId
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
                text: data.response,
                sender: 'bot',
                sources: data.sources,
                confidence: data.confidence,
                timestamp: new Date().toISOString()
            };

            setMessages((prevMessages) => [...prevMessages, botMessage]);

            // Update session ID if server provided new one
            if (data.session_id && data.session_id !== sessionId) {
                setSessionId(data.session_id);
                if (typeof window !== 'undefined') {
                    localStorage.setItem('chatSessionId', data.session_id);
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                text: error.message.includes('fetch')
                    ? 'Error: Could not connect to the chatbot server. Please make sure the backend is running.'
                    : 'Error: Could not get a response. Please try again.',
                sender: 'bot',
                timestamp: new Date().toISOString()
            };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const clearChat = () => {
        setMessages([]);
        const newSessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        setSessionId(newSessionId);
        if (typeof window !== 'undefined') {
            localStorage.setItem('chatSessionId', newSessionId);
        }
    };

    return (
        <div className={styles.chatbotContainer}>
            <div className={styles.chatHeader}>
                <h3>AI Tutor</h3>
                <button onClick={clearChat} className={styles.clearButton} title="Clear chat">
                    🗑️
                </button>
            </div>
            <div className={styles.messagesDisplay}>
                {messages.length === 0 && (
                    <div className={styles.welcomeMessage}>
                        <p>👋 Hi! I'm your AI tutor for Physical AI & Humanoid Robotics.</p>
                        <p>Ask me anything about:</p>
                        <ul>
                            <li>ROS 2 and robot control</li>
                            <li>Simulation with Gazebo & Unity</li>
                            <li>NVIDIA Isaac platform</li>
                            <li>Vision-Language-Action models</li>
                        </ul>
                        <p>You can also select text on the page and ask questions about it!</p>
                    </div>
                )}
                {messages.map((msg, index) => (
                    <div key={index} className={`${styles.message} ${styles[msg.sender]}`}>
                        <div className={styles.messageContent}>{msg.text}</div>
                        {msg.sources && msg.sources.length > 0 && (
                            <div className={styles.sources}>
                                <details>
                                    <summary>📚 Sources ({msg.sources.length})</summary>
                                    {msg.sources.map((source, idx) => (
                                        <div key={idx} className={styles.sourceItem}>
                                            <strong>{source.title}</strong>
                                            {source.score && (
                                                <span className={styles.score}>
                                                    (Relevance: {(source.score * 100).toFixed(0)}%)
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </details>
                            </div>
                        )}
                        {msg.confidence !== undefined && (
                            <div className={styles.confidence}>
                                Confidence: {(msg.confidence * 100).toFixed(0)}%
                            </div>
                        )}
                    </div>
                ))}
                {loading && (
                    <div className={`${styles.message} ${styles.bot}`}>
                        <div className={styles.loadingDots}>
                            <span>.</span><span>.</span><span>.</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className={styles.messageInputForm}>
                <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={selectedText ? "Ask about the selected text..." : "Ask about the book..."}
                    className={styles.messageInput}
                    disabled={loading}
                />
                <button type="submit" disabled={loading || !inputMessage.trim()} className={styles.sendButton}>
                    {loading ? '...' : '📤'}
                </button>
            </form>
        </div>
    );
};

export default Chatbot;
