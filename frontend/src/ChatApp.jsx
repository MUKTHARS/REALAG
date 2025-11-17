import React, { useState, useRef, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { LanguageContext } from './App';
import './ChatApp.css';

const API_BASE = 'http://localhost:8000/api/v1';

function ChatApp() {
  const { currentLanguage, setCurrentLanguage, languageConfig } = useContext(LanguageContext);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const chatContent = {
    english: {
      title: '🏠 Dubai Real Estate Agent',
      subtitle: 'Speaks English, Arabic, and Tamil',
      newChat: 'New Chat',
      send: 'Send',
      sending: 'Sending...',
      placeholder: 'Type your message here...',
      welcome: {
        title: 'Welcome! 👋',
        description: 'I\'m your multilingual real estate assistant. I can help you:',
        points: [
          'Find properties in Dubai',
          'Provide market insights',
          'Answer real estate questions',
          'Communicate in English, Arabic, or Tamil'
        ],
        question: 'How can I assist you today?'
      }
    },
    arabic: {
      title: '🏠 وكيل عقارات دبي',
      subtitle: 'يتحدث الإنجليزية، العربية، والتاميلية',
      newChat: 'محادثة جديدة',
      send: 'إرسال',
      sending: 'جاري الإرسال...',
      placeholder: 'اكتب رسالتك هنا...',
      welcome: {
        title: 'مرحباً! 👋',
        description: 'أنا مساعدك العقاري متعدد اللغات. يمكنني مساعدتك في:',
        points: [
          'العثور على عقارات في دبي',
          'تقديم رؤى حول السوق',
          'الإجابة على الأسئلة العقارية',
          'التواصل باللغة الإنجليزية، العربية، أو التاميلية'
        ],
        question: 'كيف يمكنني مساعدتك اليوم؟'
      }
    },
    tamil: {
      title: '🏠 டுபாய் ரியல் எஸ்டேட் முகவர்',
      subtitle: 'ஆங்கிலம், அரபு மற்றும் தமிழில் பேசுகிறார்',
      newChat: 'புதிய அரட்டை',
      send: 'அனுப்பவும்',
      sending: 'அனுப்பப்படுகிறது...',
      placeholder: 'உங்கள் செய்தியை இங்கே தட்டச்சு செய்க...',
      welcome: {
        title: 'வரவேற்கிறோம்! 👋',
        description: 'நான் உங்கள் பல மொழி ரியல் எஸ்டேட் உதவியாளன். நான் உங்களுக்கு உதவ முடியும்:',
        points: [
          'டுபாயில் உள்ள வீடுகளை கண்டறிய',
          'சந்தை நுண்ணறிவுகளை வழங்க',
          'ரியல் எஸ்டேட் கேள்விகளுக்கு பதிலளிக்க',
          'ஆங்கிலம், அரபு அல்லது தமிழில் தொடர்பு கொள்ள'
        ],
        question: 'இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?'
      }
    }
  };

  const content = chatContent[currentLanguage];

  useEffect(() => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
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

    const newUserMessage = { 
      type: 'user', 
      content: userMessage,
      language: currentLanguage
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const messageData = {
        message: userMessage,
        session_id: sessionId,
        language: currentLanguage
      };

      const response = await axios.post(`${API_BASE}/chat`, messageData);

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
        language: currentLanguage
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
    <div className="chat-app-full" dir={languageConfig[currentLanguage].dir}>
      {/* Chat Header */}
      <div className="chat-header">
        <div className="header-main">
          <Link to="/" className="back-button">← Home</Link>
          <h1>{content.title}</h1>
          <p>{content.subtitle}</p>
        </div>
        
        <div className="header-controls">
          <select 
            className="language-selector"
            value={currentLanguage}
            onChange={(e) => setCurrentLanguage(e.target.value)}
          >
            <option value="english">English</option>
            <option value="arabic">العربية</option>
            <option value="tamil">தமிழ்</option>
          </select>
          
          <button onClick={clearChat} className="clear-btn">
            {content.newChat}
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h3>{content.welcome.title}</h3>
            <p>{content.welcome.description}</p>
            <ul>
              {content.welcome.points.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
            <p>{content.welcome.question}</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.type === 'user' ? 'user-message' : 'agent-message'}`}
            data-language={message.language}
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

      {/* Input Container */}
      <div className="input-container">
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={content.placeholder}
          rows="2"
          disabled={isLoading}
        />
        <button 
          onClick={sendMessage} 
          disabled={isLoading || !inputMessage.trim()}
          className="send-button"
        >
          {isLoading ? content.sending : content.send}
        </button>
      </div>
    </div>
  );
}

export default ChatApp;