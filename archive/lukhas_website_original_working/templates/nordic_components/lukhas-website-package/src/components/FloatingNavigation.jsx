import { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';

const FloatingNavigation = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState('EN');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  const languages = [
    { code: 'EN', name: 'English', flag: '🇬🇧' },
    { code: 'ES', name: 'Español', flag: '🇪🇸' },
    { code: 'FR', name: 'Français', flag: '🇫🇷' },
    { code: 'DE', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'IT', name: 'Italiano', flag: '🇮🇹' },
    { code: 'PT', name: 'Português', flag: '🇵🇹' },
  ];

  useEffect(() => {
    let lastScrollY = window.scrollY;
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const currentScrollY = window.scrollY;
          
          // Hide navigation when scrolling down, show when scrolling up
          if (currentScrollY > lastScrollY && currentScrollY > 100) {
            setIsVisible(false);
          } else if (currentScrollY < lastScrollY || currentScrollY < 100) {
            setIsVisible(true);
          }
          
          lastScrollY = currentScrollY;
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navigationItems = [
    { label: 'Project', href: '#project' },
    { label: 'ΛGI System', href: '#agi-system' },
    { label: 'ΛiD System', href: '#aid-system' },
    { label: 'Rural Impact', href: '#rural-impact' },
    { label: 'Visuals', href: '#visuals' },
    { label: 'Contact', href: '#contact' },
  ];

  return (
    <nav className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-50 floating-nav rounded-full px-8 py-4 ${!isVisible ? 'hidden' : ''}`}>
      <div className="flex items-center space-x-8">
        {/* Navigation Items */}
        <div className="flex items-center space-x-6">
          {navigationItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="text-sm font-light text-slate-700 hover:text-blue-600 transition-colors duration-300 interactive-element"
              data-cursor="pointer"
            >
              {item.label}
            </a>
          ))}
        </div>

        {/* Language Selector */}
        <div className="relative">
          <button
            onClick={() => setShowLanguageMenu(!showLanguageMenu)}
            className="flex items-center space-x-2 text-sm font-light text-slate-700 hover:text-blue-600 transition-colors duration-300 interactive-element"
            data-cursor="pointer"
          >
            <Globe size={16} />
            <span>{selectedLanguage}</span>
          </button>

          {/* Language Dropdown */}
          {showLanguageMenu && (
            <div className="absolute top-full right-0 mt-2 bg-white/90 backdrop-blur-md rounded-lg shadow-lg border border-white/20 py-2 min-w-[150px]">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setSelectedLanguage(lang.code);
                    setShowLanguageMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm font-light text-slate-700 hover:bg-blue-50 hover:text-blue-600 transition-colors duration-200 flex items-center space-x-3"
                  data-cursor="pointer"
                >
                  <span>{lang.flag}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default FloatingNavigation;

