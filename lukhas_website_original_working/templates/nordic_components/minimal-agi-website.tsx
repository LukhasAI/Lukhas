import { useState, useEffect } from 'react';

export default function MinimalAgiWebsite() {
  const [currentImage, setCurrentImage] = useState(0);
  const [fadeIn, setFadeIn] = useState(true);
  
  // Earth-inspired background images
  const backgroundImages = [
    "https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?auto=format&fit=crop&q=80", // Earth from space
    "https://images.unsplash.com/photo-1574169208507-84376144848b?auto=format&fit=crop&q=80", // Nordic mountains
    "https://images.unsplash.com/photo-1486082570281-d942af5c39b7?auto=format&fit=crop&q=80", // White marble
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80"  // Space view
  ];
  
  // Handle background image transitions
  useEffect(() => {
    const interval = setInterval(() => {
      setFadeIn(false);
      setTimeout(() => {
        setCurrentImage((prev) => (prev + 1) % backgroundImages.length);
        setFadeIn(true);
      }, 1000);
    }, 8000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="relative min-h-screen font-['Inter',sans-serif] font-extralight overflow-hidden">
      {/* Background images with fade transition */}
      <div className="fixed inset-0 z-[-1]">
        {backgroundImages.map((img, index) => (
          <div 
            key={index}
            className="absolute inset-0 transition-opacity duration-1000"
            style={{ 
              backgroundImage: `url(${img})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              opacity: currentImage === index ? (fadeIn ? 1 : 0) : 0
            }}
          />
        ))}
        <div className="absolute inset-0 bg-black bg-opacity-40 backdrop-filter backdrop-blur-sm" />
      </div>
      
      {/* Main Content */}
      <div className="relative min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-8 z-10">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="text-white text-2xl tracking-[0.15em] font-extralight">
              LUKHΛS
            </div>
            
            <nav className="hidden md:flex space-x-8">
              <a href="#home" className="text-white text-opacity-80 hover:text-opacity-100 transition-opacity tracking-wider font-extralight">HOME</a>
              <a href="#about" className="text-white text-opacity-80 hover:text-opacity-100 transition-opacity tracking-wider font-extralight">ABOUT</a>
              <a href="#technology" className="text-white text-opacity-80 hover:text-opacity-100 transition-opacity tracking-wider font-extralight">TECHNOLOGY</a>
              <a href="#contact" className="text-white text-opacity-80 hover:text-opacity-100 transition-opacity tracking-wider font-extralight">CONTACT</a>
            </nav>
          </div>
        </header>
        
        {/* Hero Section */}
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-4xl text-center">
            <h1 className="text-white text-5xl md:text-8xl font-extralight tracking-widest mb-6">
              Λ
            </h1>
            <h2 className="text-white text-xl md:text-3xl font-extralight tracking-wider mb-8">
              INTELLIGENCE EVOLVED
            </h2>
            <p className="text-white text-opacity-80 max-w-xl mx-auto mb-12 leading-relaxed">
              A sophisticated approach to artificial general intelligence that adapts and evolves with the natural world.
              Designed with Earth's intelligence systems as our foundation.
            </p>
            <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-6 justify-center">
              <button className="px-8 py-3 border border-white border-opacity-30 text-white text-opacity-90 bg-black bg-opacity-20 backdrop-filter backdrop-blur-sm hover:bg-opacity-30 transition-all tracking-wider font-light">
                EXPLORE
              </button>
              <button className="px-8 py-3 border border-white border-opacity-30 text-white text-opacity-90 bg-black bg-opacity-20 backdrop-filter backdrop-blur-sm hover:bg-opacity-30 transition-all tracking-wider font-light">
                CONNECT
              </button>
            </div>
          </div>
        </main>
        
        {/* Footer */}
        <footer className="p-8">
          <div className="max-w-6xl mx-auto text-center">
            <div className="text-white text-opacity-50 text-xs tracking-wider">
              LUKHΛS SYSTEMS • EARTH DIVISION
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
