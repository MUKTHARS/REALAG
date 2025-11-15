import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Generate session ID on component mount
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    
    // Load conversation history
    loadConversationHistory(newSessionId);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateSessionId = () => {
    return 'session_' + Math.random().toString(36).substr(2, 9);
  };

const loadConversationHistory = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE}/conversations/${sessionId}`);
    console.log('Conversation history response:', response.data); // Debug log
    
    if (response.data && Array.isArray(response.data) && response.data.length > 0) {
      const history = response.data.flatMap(conv => [
        { type: 'user', content: conv.user_message, language: conv.language },
        { type: 'agent', content: conv.agent_response, language: conv.language }
      ]);
      setMessages(history);
    } else {
      setMessages([]);
    }
  } catch (error) {
    console.error('Error loading conversation history:', error);
    setMessages([]);
  }
};

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to chat
    const newUserMessage = { type: 'user', content: userMessage };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: userMessage,
        session_id: sessionId
      });

      // Add agent response to chat
      const agentMessage = {
        type: 'agent',
        content: response.data.response,
        language: response.data.language
      };
      setMessages(prev => [...prev, agentMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'agent',
        content: 'Sorry, I encountered an error. Please try again.',
        language: 'english'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <h1>🏠 Dubai Real Estate Agent</h1>
          <p>Speaks English, Arabic, and Tamil</p>
          <button onClick={clearChat} className="clear-btn">New Chat</button>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h3>Welcome! 👋</h3>
              <p>I'm your multilingual real estate assistant. I can help you:</p>
              <ul>
                <li>Find properties in Dubai</li>
                <li>Provide market insights</li>
                <li>Answer real estate questions</li>
                <li>Communicate in English, Arabic, or Tamil</li>
              </ul>
              <p>How can I assist you today?</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.type === 'user' ? 'user-message' : 'agent-message'}`}
            >
              <div className="message-content">
                {message.content}
              </div>
              {message.language && (
                <div className="language-badge">
                  {message.language}
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="message agent-message">
              <div className="message-content typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message in English, Arabic, or Tamil..."
            rows="2"
            disabled={isLoading}
          />
          <button 
            onClick={sendMessage} 
            disabled={isLoading || !inputMessage.trim()}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;