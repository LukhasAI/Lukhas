import { useEffect, useState } from 'react';

const ScrollProgress = () => {
  const [progress, setProgress] = useState(0);
  const [activeSection, setActiveSection] = useState(0);

  const sections = [
    { id: 'hero', label: 'Home' },
    { id: 'project', label: 'Project' },
    { id: 'agi-system', label: 'ΛGI' },
    { id: 'aid-system', label: 'ΛiD' },
    { id: 'rural-impact', label: 'Rural' },
    { id: 'visuals', label: 'Visuals' },
    { id: 'contact', label: 'Contact' },
  ];

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercent = scrollTop / docHeight;
      setProgress(scrollPercent);

      // Determine active section
      const sectionElements = sections.map(section => 
        document.getElementById(section.id) || document.querySelector('.hero-section')
      );

      let currentSection = 0;
      sectionElements.forEach((element, index) => {
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
            currentSection = index;
          }
        }
      });

      setActiveSection(currentSection);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll(); // Initial call

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleDotClick = (index) => {
    const section = sections[index];
    const element = section.id === 'hero' 
      ? document.querySelector('.hero-section')
      : document.getElementById(section.id);
    
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-1 bg-slate-200/30 z-50">
        <div 
          className="h-full bg-blue-600 transition-all duration-300 ease-out"
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      {/* Scroll Indicators */}
      <div className="scroll-indicator">
        {sections.map((section, index) => (
          <div
            key={section.id}
            className={`dot cursor-pointer ${index === activeSection ? 'active' : ''}`}
            onClick={() => handleDotClick(index)}
            title={section.label}
            data-cursor="pointer"
          />
        ))}
      </div>
    </>
  );
};

export default ScrollProgress;

