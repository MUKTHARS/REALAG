import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import axios from 'axios';
import HomePage from './HomePage';
import ChatApp from './ChatApp';
import './App.css';

// Language Context
export const LanguageContext = React.createContext();

function App() {
  const [currentLanguage, setCurrentLanguage] = useState('english');
  
  const languageConfig = {
    english: { code: 'en', name: 'English', dir: 'ltr' },
    arabic: { code: 'ar', name: 'العربية', dir: 'rtl' },
    tamil: { code: 'ta', name: 'தமிழ்', dir: 'ltr' }
  };

  useEffect(() => {
    document.documentElement.dir = languageConfig[currentLanguage].dir;
  }, [currentLanguage]);

  return (
    <LanguageContext.Provider value={{ currentLanguage, setCurrentLanguage, languageConfig }}>
      <Router>
        <div className="app">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatApp />} />
          </Routes>
        </div>
      </Router>
    </LanguageContext.Provider>
  );
}

export default App;

// import React, { useState, useRef, useEffect } from 'react';
// import axios from 'axios';
// import './App.css';

// const API_BASE = 'http://localhost:8000/api/v1';

// function App() {
//   const [messages, setMessages] = useState([]);
//   const [inputMessage, setInputMessage] = useState('');
//   const [sessionId, setSessionId] = useState(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const [selectedLanguage, setSelectedLanguage] = useState('auto'); // 'auto', 'english', 'arabic', 'tamil'
//   const messagesEndRef = useRef(null);

//   useEffect(() => {
//     // Generate session ID on component mount
//     const newSessionId = generateSessionId();
//     setSessionId(newSessionId);
    
//     // Load conversation history
//     loadConversationHistory(newSessionId);
//   }, []);

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const generateSessionId = () => {
//     return 'session_' + Math.random().toString(36).substr(2, 9);
//   };

//   const loadConversationHistory = async (sessionId) => {
//     try {
//       const response = await axios.get(`${API_BASE}/conversations/${sessionId}`);
//       console.log('Conversation history response:', response.data);
      
//       if (response.data && Array.isArray(response.data) && response.data.length > 0) {
//         const history = response.data.flatMap(conv => [
//           { type: 'user', content: conv.user_message, language: conv.language },
//           { type: 'agent', content: conv.agent_response, language: conv.language }
//         ]);
//         setMessages(history);
//       } else {
//         setMessages([]);
//       }
//     } catch (error) {
//       console.error('Error loading conversation history:', error);
//       setMessages([]);
//     }
//   };

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };

//   const sendMessage = async () => {
//     if (!inputMessage.trim() || isLoading) return;

//     const userMessage = inputMessage.trim();
//     setInputMessage('');
//     setIsLoading(true);

//     // Add user message to chat with language preference
//     const newUserMessage = { 
//       type: 'user', 
//       content: userMessage,
//       language: selectedLanguage === 'auto' ? 'detecting...' : selectedLanguage
//     };
//     setMessages(prev => [...prev, newUserMessage]);

//     try {
//       // Prepare message data with language preference
//       const messageData = {
//         message: userMessage,
//         session_id: sessionId
//       };

//       // If a specific language is selected (not auto), add it to the message
//       if (selectedLanguage !== 'auto') {
//         // You can add language hint to the message to help the AI
//         const languageHint = `[Please respond in ${selectedLanguage}] `;
//         messageData.message = languageHint + userMessage;
//       }

//       const response = await axios.post(`${API_BASE}/chat`, messageData);

//       // Add agent response to chat
//       const agentMessage = {
//         type: 'agent',
//         content: response.data.response,
//         language: response.data.language
//       };
//       setMessages(prev => [...prev, agentMessage]);

//     } catch (error) {
//       console.error('Error sending message:', error);
//       const errorMessage = {
//         type: 'agent',
//         content: 'Sorry, I encountered an error. Please try again.',
//         language: 'english'
//       };
//       setMessages(prev => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       sendMessage();
//     }
//   };

//   const clearChat = () => {
//     setMessages([]);
//     const newSessionId = generateSessionId();
//     setSessionId(newSessionId);
//   };

//   const handleLanguageChange = (language) => {
//     setSelectedLanguage(language);
//   };

//   // Get header content based on selected language
//   const getHeaderContent = () => {
//     switch (selectedLanguage) {
//       case 'arabic':
//         return {
//           title: '🏠 وكيل عقارات دبي',
//           subtitle: 'يتحدث الإنجليزية، العربية، والتاميلية',
//           newChat: 'محادثة جديدة',
//           send: 'إرسال',
//           sending: 'جاري الإرسال...'
//         };
//       case 'tamil':
//         return {
//           title: '🏠 டுபாய் ரியல் எஸ்டேட் முகவர்',
//           subtitle: 'ஆங்கிலம், அரபு மற்றும் தமிழில் பேசுகிறார்',
//           newChat: 'புதிய அரட்டை',
//           send: 'அனுப்பவும்',
//           sending: 'அனுப்பப்படுகிறது...'
//         };
//       default:
//         return {
//           title: '🏠 Dubai Real Estate Agent',
//           subtitle: 'Speaks English, Arabic, and Tamil',
//           newChat: 'New Chat',
//           send: 'Send',
//           sending: 'Sending...'
//         };
//     }
//   };

//   // Get welcome message based on selected language
//   const getWelcomeMessage = () => {
//     switch (selectedLanguage) {
//       case 'arabic':
//         return {
//           title: 'مرحباً! 👋',
//           description: 'أنا مساعدك العقاري متعدد اللغات. يمكنني مساعدتك في:',
//           points: [
//             'العثور على عقارات في دبي',
//             'تقديم رؤى حول السوق',
//             'الإجابة على الأسئلة العقارية',
//             'التواصل باللغة الإنجليزية، العربية، أو التاميلية'
//           ],
//           question: 'كيف يمكنني مساعدتك اليوم؟'
//         };
//       case 'tamil':
//         return {
//           title: 'வரவேற்கிறோம்! 👋',
//           description: 'நான் உங்கள் பல மொழி ரியல் எஸ்டேட் உதவியாளன். நான் உங்களுக்கு உதவ முடியும்:',
//           points: [
//             'டுபாயில் உள்ள வீடுகளை கண்டறிய',
//             'சந்தை நுண்ணறிவுகளை வழங்க',
//             'ரியல் எஸ்டேட் கேள்விகளுக்கு பதிலளிக்க',
//             'ஆங்கிலம், அரபு அல்லது தமிழில் தொடர்பு கொள்ள'
//           ],
//           question: 'இன்று நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?'
//         };
//       default:
//         return {
//           title: 'Welcome! 👋',
//           description: 'I\'m your multilingual real estate assistant. I can help you:',
//           points: [
//             'Find properties in Dubai',
//             'Provide market insights',
//             'Answer real estate questions',
//             'Communicate in English, Arabic, or Tamil'
//           ],
//           question: 'How can I assist you today?'
//         };
//     }
//   };

//   const headerContent = getHeaderContent();
//   const welcomeContent = getWelcomeMessage();

//   // Get language options for dropdown
//   const getLanguageOptions = () => {
//     switch (selectedLanguage) {
//       case 'arabic':
//         return [
//           // { value: 'auto', label: 'الكشف التلقائي' },
//           { value: 'english', label: 'الإنجليزية' },
//           { value: 'arabic', label: 'العربية' },
//           { value: 'tamil', label: 'التاميلية' }
//         ];
//       case 'tamil':
//         return [
//           // { value: 'auto', label: 'தானாக கண்டறிதல்' },
//           { value: 'english', label: 'ஆங்கிலம்' },
//           { value: 'arabic', label: 'அரபு' },
//           { value: 'tamil', label: 'தமிழ்' }
//         ];
//       default:
//         return [
//           // { value: 'auto', label: 'Auto Detect' },
//           { value: 'english', label: 'English' },
//           { value: 'arabic', label: 'العربية (Arabic)' },
//           { value: 'tamil', label: 'தமிழ் (Tamil)' }
//         ];
//     }
//   };

//   const languageOptions = getLanguageOptions();

//   return (
//     <div className="app">
//       <div className="chat-container">
//         <div className="chat-header">
//           <div className="header-main">
//             <h1>{headerContent.title}</h1>
//             <p>{headerContent.subtitle}</p>
//           </div>
          
//           {/* Language Selector */}
//           <div className="header-controls">
//             <div className="language-selector">
//               <label>
//                 {selectedLanguage === 'arabic' ? 'اللغة: ' : 
//                  selectedLanguage === 'tamil' ? 'மொழி: ' : 'Language: '}
//               </label>
//               <select 
//                 value={selectedLanguage} 
//                 onChange={(e) => handleLanguageChange(e.target.value)}
//                 className="language-dropdown"
//               >
//                 {languageOptions.map(option => (
//                   <option key={option.value} value={option.value}>
//                     {option.label}
//                   </option>
//                 ))}
//               </select>
//             </div>
            
//             <button onClick={clearChat} className="clear-btn">
//               {headerContent.newChat}
//             </button>
//           </div>
//         </div>

//         <div className="messages-container">
//           {messages.length === 0 && (
//             <div 
//               className="welcome-message"
//               dir={selectedLanguage === 'arabic' ? 'rtl' : 'ltr'}
//             >
//               <h3>{welcomeContent.title}</h3>
//               <p>{welcomeContent.description}</p>
//               <ul>
//                 {welcomeContent.points.map((point, index) => (
//                   <li key={index}>{point}</li>
//                 ))}
//               </ul>
//               <p>{welcomeContent.question}</p>
//             </div>
//           )}
          
//           {messages.map((message, index) => (
//             <div
//               key={index}
//               className={`message ${message.type === 'user' ? 'user-message' : 'agent-message'}`}
//               data-language={message.language}
//               dir={message.language === 'arabic' ? 'rtl' : 'ltr'}
//             >
//               <div className="message-content">
//                 {message.content}
//               </div>
//               {message.language && (
//                 <div className="language-badge">
//                   {message.language}
//                 </div>
//               )}
//             </div>
//           ))}
          
//           {isLoading && (
//             <div className="message agent-message">
//               <div className="message-content typing-indicator">
//                 <span></span>
//                 <span></span>
//                 <span></span>
//               </div>
//             </div>
//           )}
          
//           <div ref={messagesEndRef} />
//         </div>

//         <div className="input-container">
//           <textarea
//             value={inputMessage}
//             onChange={(e) => setInputMessage(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder={
//               selectedLanguage === 'arabic' 
//                 ? 'اكتب رسالتك هنا...' 
//                 : selectedLanguage === 'tamil'
//                 ? 'உங்கள் செய்தியை இங்கே தட்டச்சு செய்க...'
//                 : 'Type your message here...'
//             }
//             rows="2"
//             disabled={isLoading}
//             dir={selectedLanguage === 'arabic' ? 'rtl' : 'ltr'}
//           />
//           <button 
//             onClick={sendMessage} 
//             disabled={isLoading || !inputMessage.trim()}
//           >
//             {isLoading ? headerContent.sending : headerContent.send}
//           </button>
//         </div>
//       </div>
//     </div>//
//   );
// }

// export default App;