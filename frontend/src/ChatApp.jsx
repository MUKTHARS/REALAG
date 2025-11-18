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
  const [chatHistory, setChatHistory] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [authData, setAuthData] = useState({ email: '', password: '', name: '' });
  const messagesEndRef = useRef(null);

  const chatContent = {
    english: {
      title: 'Homeiq AI',
      newChat: 'New Chat',
      send: 'Send',
      sending: 'Sending...',
      placeholder: 'Type your message...',
      welcome: 'How can I help you with Dubai real estate today?',
      chatHistory: 'Chat History',
      noChats: 'No previous chats',
      toggleHistory: 'History',
      login: 'Login',
      signup: 'Sign Up',
      logout: 'Logout',
      email: 'Email',
      password: 'Password',
      name: 'Full Name',
      loginTitle: 'Login to Your Account',
      signupTitle: 'Create New Account',
      or: 'or',
      googleLogin: 'Continue with Google',
      guestMode: 'Continue as Guest',
      noAccount: "Don't have an account?",
      hasAccount: "Already have an account?"
    },
    arabic: {
      title: 'دبي إستيت الذكية',
      newChat: 'محادثة جديدة',
      send: 'إرسال',
      sending: 'جاري الإرسال...',
      placeholder: 'اكتب رسالتك...',
      welcome: 'كيف يمكنني مساعدتك في عقارات دبي اليوم؟',
      chatHistory: 'سجل المحادثات',
      noChats: 'لا توجد محادثات سابقة',
      toggleHistory: 'السجل',
      login: 'تسجيل الدخول',
      signup: 'إنشاء حساب',
      logout: 'تسجيل الخروج',
      email: 'البريد الإلكتروني',
      password: 'كلمة المرور',
      name: 'الاسم الكامل',
      loginTitle: 'تسجيل الدخول إلى حسابك',
      signupTitle: 'إنشاء حساب جديد',
      or: 'أو',
      googleLogin: 'المتابعة مع جوجل',
      guestMode: 'المتابعة كزائر',
      noAccount: 'ليس لديك حساب؟',
      hasAccount: 'لديك حساب بالفعل؟'
    },
    tamil: {
      title: 'டுபாய் எஸ்டேட் AI',
      newChat: 'புதிய அரட்டை',
      send: 'அனுப்பவும்',
      sending: 'அனுப்பப்படுகிறது...',
      placeholder: 'உங்கள் செய்தியை தட்டச்சு செய்க...',
      welcome: 'இன்று டுபாய் ரியல் எஸ்டேட்டில் நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?',
      chatHistory: 'அரட்டை வரலாறு',
      noChats: 'முந்தைய அரட்டைகள் இல்லை',
      toggleHistory: 'வரலாறு',
      login: 'உள்நுழைக',
      signup: 'புதிய கணக்கு',
      logout: 'வெளியேறு',
      email: 'மின்னஞ்சல்',
      password: 'கடவுச்சொல்',
      name: 'முழு பெயர்',
      loginTitle: 'உங்கள் கணக்கில் உள்நுழைக',
      signupTitle: 'புதிய கணக்கை உருவாக்குக',
      or: 'அல்லது',
      googleLogin: 'Google உடன் தொடர்க',
      guestMode: 'விருந்தினராக தொடர்க',
      noAccount: 'கணக்கு இல்லையா?',
      hasAccount: 'ஏற்கனவே கணக்கு உள்ளதா?'
    }
  };

  const content = chatContent[currentLanguage];

useEffect(() => {
  // Check if user is logged in from localStorage
  const savedUser = localStorage.getItem('user');
  const savedSessionId = localStorage.getItem('currentSessionId');
  const savedMessages = localStorage.getItem('currentChatMessages');
  
  if (savedUser) {
    try {
      const userData = JSON.parse(savedUser);
      setUser(userData);
      console.log('User loaded from localStorage:', userData);
    } catch (e) {
      console.error('Error parsing saved user:', e);
      localStorage.removeItem('user');
    }
  }
  
  // Load session and messages
  if (savedSessionId) {
    setSessionId(savedSessionId);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Error parsing saved messages:', e);
        setMessages([]);
      }
    }
  } else {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    localStorage.setItem('currentSessionId', newSessionId);
  }
}, []);

  useEffect(() => {
    scrollToBottom();
    // Save messages to localStorage whenever they change
    if (messages.length > 0) {
      localStorage.setItem('currentChatMessages', JSON.stringify(messages));
    }
  }, [messages]);

  const generateSessionId = () => {
    return 'session_' + Math.random().toString(36).substr(2, 9);
  };

  const loadConversationHistory = async (sessionId) => {
    if (!user) return;
    
    try {
      const response = await axios.get(`${API_BASE}/conversations/${sessionId}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        const history = response.data.flatMap(conv => [
          { type: 'user', content: conv.user_message, language: conv.language },
          { type: 'agent', content: conv.agent_response, language: conv.language }
        ]);
        setMessages(history);
        localStorage.setItem('currentChatMessages', JSON.stringify(history));
      } else {
        setMessages([]);
        localStorage.removeItem('currentChatMessages');
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
      setMessages([]);
    }
  };

const loadChatHistory = async () => {
  if (!user || !user.token) {
    console.log('No user or token found, skipping chat history load');
    return;
  }
  
  try {
    console.log('Loading chat history for user:', user.id);
    const response = await axios.get(`${API_BASE}/chat-sessions`, {
      headers: { Authorization: `Bearer ${user.token}` },
      params: { user_id: user.id }
    });
    
    if (response.data && response.data.sessions) {
      console.log('Chat history loaded:', response.data.sessions.length, 'sessions');
      setChatHistory(response.data.sessions);
      localStorage.setItem('chatHistory', JSON.stringify(response.data.sessions));
    }
  } catch (error) {
    console.error('Error loading chat history:', error);
    // Keep existing history if available
    if (!chatHistory.length) {
      setChatHistory([]);
    }
  }
};

useEffect(() => {
  if (user && user.token) {
    console.log('User authenticated, loading chat history');
    loadChatHistory();
  } else {
    console.log('No user, clearing chat history');
    setChatHistory([]);
  }
}, [user]);


useEffect(() => {
  if (user) {
    console.log('User state changed, loading chat history');
    loadChatHistory();
  }
}, [user]);

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
  const updatedMessages = [...messages, newUserMessage];
  setMessages(updatedMessages);
  localStorage.setItem('currentChatMessages', JSON.stringify(updatedMessages));

  try {
    const messageData = {
      message: userMessage,
      session_id: sessionId,
      language: currentLanguage
    };

    const config = user ? { 
      headers: { Authorization: `Bearer ${user.token}` },
      params: {
        user_id: user.id  // Send user_id as query parameter in POST request
      }
    } : {};

    const response = await axios.post(`${API_BASE}/chat`, messageData, config);

    const agentMessage = {
      type: 'agent',
      content: response.data.response,
      language: response.data.language
    };
    const finalMessages = [...updatedMessages, agentMessage];
    setMessages(finalMessages);
    localStorage.setItem('currentChatMessages', JSON.stringify(finalMessages));

    // Reload chat history to update the sidebar with user-specific data
    if (user) {
      loadChatHistory();
    }

  } catch (error) {
    console.error('Error sending message:', error);
    const errorMessage = {
      type: 'agent',
      content: 'Sorry, I encountered an error. Please try again.',
      language: currentLanguage
    };
    const errorMessages = [...updatedMessages, errorMessage];
    setMessages(errorMessages);
    localStorage.setItem('currentChatMessages', JSON.stringify(errorMessages));
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
    localStorage.removeItem('currentChatMessages');
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    localStorage.setItem('currentSessionId', newSessionId);
  };

const handleAuth = async (e) => {
  e.preventDefault();
  try {
    const endpoint = isLogin ? '/auth/login' : '/auth/signup';
    console.log('Attempting authentication:', endpoint, authData);
    
    const response = await axios.post(`${API_BASE}${endpoint}`, authData);
    
    console.log('Authentication successful:', response.data);
    
    const userData = { 
      ...response.data.user, 
      token: response.data.token 
    };
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    setShowAuthModal(false);
    setAuthData({ email: '', password: '', name: '' });
    
    // Load chat history immediately after login
    await loadChatHistory();
    
  } catch (error) {
    console.error('Authentication error details:', error);
    console.error('Error response:', error.response?.data);
    
    let errorMessage = 'Authentication failed. Please try again.';
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.status === 401) {
      errorMessage = 'Invalid email or password.';
    } else if (error.response?.status === 400) {
      errorMessage = 'Email already registered. Please use a different email.';
    }
    
    alert(errorMessage);
  }
};

const handleGoogleLogin = () => {
  // Simulate OAuth login - in real app, this would redirect to OAuth provider
  const mockUser = {
    id: 1,
    name: 'Google User',
    email: 'user@gmail.com',
    token: 'google_oauth_token_' + Math.random().toString(36).substr(2, 9)
  };
  setUser(mockUser);
  localStorage.setItem('user', JSON.stringify(mockUser));
  setShowAuthModal(false);
  
  // Load chat history immediately after Google login
  setTimeout(() => {
    loadChatHistory();
  }, 100);
};

  const handleGuestMode = () => {
    setShowAuthModal(false);
    // Guest mode - no user data saved
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('currentSessionId');
    localStorage.removeItem('currentChatMessages');
    localStorage.removeItem('chatHistory');
    setMessages([]);
    setChatHistory([]);
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    localStorage.setItem('currentSessionId', newSessionId);
  };

  const loadChat = async (chatSession) => {
    try {
      // Load conversation history for the selected chat session
      const response = await axios.get(`${API_BASE}/conversations/${chatSession.session_id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      
      if (response.data && Array.isArray(response.data)) {
        const history = response.data.flatMap(conv => [
          { type: 'user', content: conv.user_message, language: conv.language },
          { type: 'agent', content: conv.agent_response, language: conv.language }
        ]);
        setMessages(history);
        setSessionId(chatSession.session_id);
        localStorage.setItem('currentSessionId', chatSession.session_id);
        localStorage.setItem('currentChatMessages', JSON.stringify(history));
      }
      
      setIsSidebarOpen(false);
    } catch (error) {
      console.error('Error loading chat:', error);
      alert('Error loading chat history');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-app-simple" dir={languageConfig[currentLanguage].dir}>
      {/* Auth Modal */}
      {showAuthModal && (
        <div className="auth-modal-overlay">
          <div className="auth-modal">
            <div className="auth-header">
              <h3>{isLogin ? content.loginTitle : content.signupTitle}</h3>
              <button 
                className="close-auth"
                onClick={() => setShowAuthModal(false)}
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleAuth} className="auth-form">
              {!isLogin && (
                <div className="form-group">
                  <label>{content.name}</label>
                  <input
                    type="text"
                    value={authData.name}
                    onChange={(e) => setAuthData({...authData, name: e.target.value})}
                    required={!isLogin}
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>{content.email}</label>
                <input
                  type="email"
                  value={authData.email}
                  onChange={(e) => setAuthData({...authData, email: e.target.value})}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>{content.password}</label>
                <input
                  type="password"
                  value={authData.password}
                  onChange={(e) => setAuthData({...authData, password: e.target.value})}
                  required
                />
              </div>
              
              <button type="submit" className="auth-submit-btn">
                {isLogin ? content.login : content.signup}
              </button>
            </form>
            
            <div className="auth-divider">
              <span>{content.or}</span>
            </div>
            
            <div className="auth-options">
              <button className="oauth-btn google-btn" onClick={handleGoogleLogin}>
                {content.googleLogin}
              </button>
              <button className="guest-btn" onClick={handleGuestMode}>
                {content.guestMode}
              </button>
            </div>
            
            <div className="auth-switch">
              <p>
                {isLogin ? content.noAccount : content.hasAccount}
                <button 
                  type="button" 
                  className="switch-mode-btn"
                  onClick={() => setIsLogin(!isLogin)}
                >
                  {isLogin ? content.signup : content.login}
                </button>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar - Only show if user is logged in */}
      {user && (
        <div className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
          <div className="sidebar-header">
            <h3>{content.chatHistory}</h3>
            <button 
              className="close-sidebar"
              onClick={() => setIsSidebarOpen(false)}
            >
              ×
            </button>
          </div>
          <div className="chat-history-list">
            {chatHistory.length === 0 ? (
              <div className="no-chats">{content.noChats}</div>
            ) : (
              chatHistory.map(chat => (
                <div 
                  key={chat.id} 
                  className={`chat-history-item ${sessionId === chat.session_id ? 'active' : ''}`}
                  onClick={() => loadChat(chat)}
                >
                  <div className="chat-title">{chat.title}</div>
                  <div className="chat-meta">
                    <span className="chat-date">{formatDate(chat.updated_at || chat.created_at)}</span>
                    <span className="message-count">{chat.message_count} messages</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Simple Header */}
        <div className="chat-header-simple">
          <div className="header-left">
            {user && (
              <button 
                className="menu-btn"
                onClick={() => setIsSidebarOpen(true)}
              >
                ☰
              </button>
            )}
            <Link to="/"></Link>
            <span className="chat-title">{content.title}</span>
          </div>
          <div className="header-right">
            <select 
              className="lang-select"
              value={currentLanguage}
              onChange={(e) => setCurrentLanguage(e.target.value)}
            >
              <option value="english">EN</option>
              <option value="arabic">AR</option>
              <option value="tamil">TA</option>
            </select>
            
            {user ? (
              <>
                <button onClick={clearChat} className="new-chat-btn">
                  {content.newChat}
                </button>
                <button onClick={handleLogout} className="logout-btn">
                  {content.logout}
                </button>
                <span className="user-name">{user.name}</span>
              </>
            ) : (
              <button 
                onClick={() => setShowAuthModal(true)} 
                className="login-btn"
              >
                {content.login}
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.length === 0 && (
            <div className="welcome-simple">
              <div className="welcome-icon">🪎</div>
              <p>{content.welcome}</p>
              {/* {!user && (
                <div className="guest-notice">
                  <p>You are in guest mode. Login to save your chat history.</p>
                  <button 
                    onClick={() => setShowAuthModal(true)}
                    className="guest-login-btn"
                  >
                    Login to Save Chats
                  </button>
                </div>
              )} */}
            </div>
          )}
          
          <div className="messages-list-simple">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-simple ${message.type === 'user' ? 'user-msg' : 'ai-msg'}`}
              >
                <div className="msg-content">
                  {message.content}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message-simple ai-msg">
                <div className="typing-simple">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-area-simple">
          <div className="input-container-simple">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={content.placeholder}
              rows="1"
              disabled={isLoading}
            />
            <button 
              onClick={sendMessage} 
              disabled={isLoading || !inputMessage.trim()}
              className="send-btn-simple"
            >
              {isLoading ? content.sending : content.send}
            </button>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && user && (
        <div 
          className="sidebar-overlay"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}

export default ChatApp;