import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const [currentLanguage, setCurrentLanguage] = useState('english');
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const languages = {
    english: { code: 'en', name: 'English', dir: 'ltr' },
    arabic: { code: 'ar', name: 'العربية', dir: 'rtl' },
    tamil: { code: 'ta', name: 'தமிழ்', dir: 'ltr' }
  };

  const content = {
    english: {
      nav: {
        home: 'Home',
        about: 'About',
        chat: 'Chat Agent',
        contact: 'Contact'
      },
      hero: {
        title: 'AI-Powered Real Estate Intelligence',
        subtitle: 'Multilingual property insights and market analysis powered by advanced AI',
        cta: 'Start Chatting',
        secondary: 'Learn More'
      },
      features: {
        title: 'Enterprise-Grade Solutions',
        items: [
          {
            title: 'Multilingual Support',
            description: 'Communicate seamlessly in English, Arabic, and Tamil with native-level fluency'
          },
          {
            title: 'Market Intelligence',
            description: 'Real-time property insights and comprehensive market analysis'
          },
          {
            title: '24/7 Availability',
            description: 'Round-the-clock assistance for all your real estate queries'
          },
          {
            title: 'Smart Matching',
            description: 'AI-powered property recommendations based on your preferences'
          }
        ]
      },
      about: {
        title: 'About DubaiEstate AI',
        description: 'We revolutionize real estate interactions through advanced artificial intelligence. Our multilingual AI agent provides instant, accurate property information and market insights across Dubai\'s dynamic real estate landscape.',
        mission: 'Our mission is to make real estate intelligence accessible to everyone, breaking language barriers and providing expert insights 24/7.',
        stats: [
          { value: '10K+', label: 'Properties Analyzed' },
          { value: '3', label: 'Languages Supported' },
          { value: '24/7', label: 'Availability' },
          { value: '99%', label: 'Accuracy Rate' }
        ]
      },
      footer: {
        description: 'Advanced AI Real Estate Assistant',
        rights: 'All rights reserved.'
      }
    },
    arabic: {
      nav: {
        home: 'الرئيسية',
        about: 'من نحن',
        chat: 'الدردشة',
        contact: 'اتصل بنا'
      },
      hero: {
        title: 'الذكاء العقاري المدعوم بالذكاء الاصطناعي',
        subtitle: 'رؤى عقارية متعددة اللغات وتحليل السوق مدعوم بالذكاء الاصطناعي المتقدم',
        cta: 'ابدأ المحادثة',
        secondary: 'اعرف المزيد'
      },
      features: {
        title: 'حلول مستوى المؤسسات',
        items: [
          {
            title: 'دعم متعدد اللغات',
            description: 'تواصل بسلاسة باللغات الإنجليزية والعربية والتاميلية بطلاقة محلية'
          },
          {
            title: 'ذكاء السوق',
            description: 'رؤى عقارية فورية وتحليل شامل للسوق'
          },
          {
            title: 'متاح 24/7',
            description: 'مساعدة على مدار الساعة لجميع استفساراتك العقارية'
          },
          {
            title: 'مطابقة ذكية',
            description: 'توصيات عقارية مدعومة بالذكاء الاصطناعي بناءً على تفضيلاتك'
          }
        ]
      },
      about: {
        title: 'عن دبي إستيت الذكية',
        description: 'نحدث ثورة في التفاعلات العقارية من خلال الذكاء الاصطناعي المتقدم. يقدم وكيلنا للذكاء الاصطناعي متعدد اللغات معلومات عقارية فورية ودقيقة ورؤى للسوق عبر المشهد العقاري الديناميكي في دبي.',
        mission: 'مهمتنا هي جعل الذكاء العقاري في متناول الجميع، وكسر حواجز اللغة وتقديم رؤى الخبراء على مدار 24 ساعة.',
        stats: [
          { value: '١٠ آلاف+', label: 'عقار تم تحليله' },
          { value: '٣', label: 'لغات مدعومة' },
          { value: '٢٤/٧', label: 'التوفر' },
          { value: '٩٩٪', label: 'معدل الدقة' }
        ]
      },
      footer: {
        description: 'مساعد عقاري ذكي متقدم',
        rights: 'جميع الحقوق محفوظة.'
      }
    },
    tamil: {
      nav: {
        home: 'முகப்பு',
        about: 'எங்களைப் பற்றி',
        chat: 'அரட்டை',
        contact: 'தொடர்பு கொள்ள'
      },
      hero: {
        title: 'AI-சக்தி பெற்ற ரியல் எஸ்டேட் நுண்ணறிவு',
        subtitle: 'பல மொழி சொத்து நுண்ணறிவுகள் மற்றும் சந்தை பகுப்பாய்வு மேம்பட்ட AI மூலம் இயக்கப்படுகிறது',
        cta: 'அரட்டையைத் தொடங்கவும்',
        secondary: 'மேலும் அறிக'
      },
      features: {
        title: 'நிறுவன தர தீர்வுகள்',
        items: [
          {
            title: 'பல மொழி ஆதரவு',
            description: 'ஆங்கிலம், அரபு மற்றும் தமிழில் சொந்த மட்ட திறமையுடன் தடையின்றி தொடர்பு கொள்ளவும்'
          },
          {
            title: 'சந்தை நுண்ணறிவு',
            description: 'நிகழ்நேர சொத்து நுண்ணறிவுகள் மற்றும் விரிவான சந்தை பகுப்பாய்வு'
          },
          {
            title: '24/7 கிடைக்கும் தன்மை',
            description: 'உங்கள் அனைத்து ரியல் எஸ்டேட் வினாக்களுக்கும் நாள் முழுவதும் உதவி'
          },
          {
            title: 'ஸ்மார்ட் பொருத்தம்',
            description: 'உங்கள் விருப்பங்களின் அடிப்படையில் AI-சக்தி பெற்ற சொத்து பரிந்துரைகள்'
          }
        ]
      },
      about: {
        title: 'டுபாய் எஸ்டேட் AI பற்றி',
        description: 'மேம்பட்ட செயற்கை நுண்ணறிவு மூலம் ரியல் எஸ்டேட் தொடர்புகளில் புரட்சியை ஏற்படுத்துகிறோம். எங்கள் பல மொழி AI முகவர் டுபாயின் மாறும் ரியல் எஸ்டேட் இயற்கைக்காட்சி முழுவதும் உடனடியான, துல்லியமான சொத்து தகவல் மற்றும் சந்தை நுண்ணறிவுகளை வழங்குகிறார்.',
        mission: 'அனைவருக்கும் ரியல் எஸ்டேட் நுண்ணறிவை அணுகக்கூடியதாக மாற்றுவதே எங்கள் நோக்கம், மொழி தடைகளை உடைத்து, நிபுணத்துவ நுண்ணறிவுகளை 24/7 வழங்குவது.',
        stats: [
          { value: '10K+', label: 'பகுப்பாய்வு செய்யப்பட்ட வீடுகள்' },
          { value: '3', label: 'ஆதரிக்கப்படும் மொழிகள்' },
          { value: '24/7', label: 'கிடைக்கும் தன்மை' },
          { value: '99%', label: 'துல்லிய விகிதம்' }
        ]
      },
      footer: {
        description: 'மேம்பட்ட AI ரியல் எஸ்டேட் உதவியாளர்',
        rights: 'அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.'
      }
    }
  };

  const currentContent = content[currentLanguage];

  useEffect(() => {
    document.documentElement.dir = languages[currentLanguage].dir;
  }, [currentLanguage]);

  return (
    <div className="homepage" dir={languages[currentLanguage].dir}>
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-icon">🏢</span>
            <span className="logo-text">DubaiEstate AI</span>
          </div>
          
          <div className="nav-links">
            <a href="#home">{currentContent.nav.home}</a>
            <a href="#about">{currentContent.nav.about}</a>
            <Link to="/chat">{currentContent.nav.chat}</Link>
            <a href="#contact">{currentContent.nav.contact}</a>
          </div>

          <div className="nav-controls">
            <select 
              className="language-selector"
              value={currentLanguage}
              onChange={(e) => setCurrentLanguage(e.target.value)}
            >
              <option value="english">English</option>
              <option value="arabic">العربية</option>
              <option value="tamil">தமிழ்</option>
            </select>
            
            <Link to="/chat" className="cta-button primary">
              {currentContent.nav.chat}
            </Link>
            
            <button 
              className="menu-toggle"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              ☰
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="mobile-menu">
            <a href="#home" onClick={() => setIsMenuOpen(false)}>{currentContent.nav.home}</a>
            <a href="#about" onClick={() => setIsMenuOpen(false)}>{currentContent.nav.about}</a>
            <Link to="/chat" onClick={() => setIsMenuOpen(false)}>{currentContent.nav.chat}</Link>
            <a href="#contact" onClick={() => setIsMenuOpen(false)}>{currentContent.nav.contact}</a>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section id="home" className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              {currentContent.hero.title}
            </h1>
            <p className="hero-subtitle">
              {currentContent.hero.subtitle}
            </p>
            <div className="hero-actions">
              <Link to="/chat" className="cta-button primary large">
                {currentContent.hero.cta}
              </Link>
              <a href="#about" className="cta-button secondary large">
                {currentContent.hero.secondary}
              </a>
            </div>
          </div>
          <div className="hero-visual">
            <div className="ai-visual">
              <div className="chat-preview">
                <div className="message user">Find apartments in Downtown Dubai</div>
                <div className="message ai">I found 15 luxury apartments in Downtown Dubai starting from AED 1.2M...</div>
                <div className="message user">Show me 2-bedroom options</div>
                <div className="message ai typing">● ● ●</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">{currentContent.features.title}</h2>
          <div className="features-grid">
            {currentContent.features.items.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">
                  {index === 0 && '🌐'}
                  {index === 1 && '📊'}
                  {index === 2 && '⏰'}
                  {index === 3 && '🎯'}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="about-section">
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2 className="section-title">{currentContent.about.title}</h2>
              <p className="about-description">
                {currentContent.about.description}
              </p>
              <p className="about-mission">
                {currentContent.about.mission}
              </p>
              
              <div className="stats-grid">
                {currentContent.about.stats.map((stat, index) => (
                  <div key={index} className="stat-item">
                    <div className="stat-value">{stat.value}</div>
                    <div className="stat-label">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="about-visual">
              <div className="visual-card">
                <div className="globe-animation">
                  <div className="orbit orbit-1"></div>
                  <div className="orbit orbit-2"></div>
                  <div className="orbit orbit-3"></div>
                  <div className="center-globe">AI</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="nav-logo">
                <span className="logo-icon">🏢</span>
                <span className="logo-text">DubaiEstate AI</span>
              </div>
              <p>{currentContent.footer.description}</p>
            </div>
            
            <div className="footer-links">
              <div className="link-group">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <Link to="/chat">Chat Agent</Link>
                <a href="#api">API</a>
              </div>
              
              <div className="link-group">
                <h4>Company</h4>
                <a href="#about">About</a>
                <a href="#careers">Careers</a>
                <a href="#contact">Contact</a>
              </div>
              
              <div className="link-group">
                <h4>Support</h4>
                <a href="#help">Help Center</a>
                <a href="#privacy">Privacy</a>
                <a href="#terms">Terms</a>
              </div>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2024 DubaiEstate AI. {currentContent.footer.rights}</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;