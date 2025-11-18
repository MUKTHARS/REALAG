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
