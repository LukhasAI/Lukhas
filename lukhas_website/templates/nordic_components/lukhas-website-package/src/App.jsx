import { useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import CustomCursor from './components/CustomCursor';
import FloatingNavigation from './components/FloatingNavigation';
import HeroSection from './components/HeroSection';
import SmoothScroll from './components/SmoothScroll';
import ScrollProgress from './components/ScrollProgress';
import EnhancedSection from './components/EnhancedSection';
import HorizontalScrollSection from './components/HorizontalScrollSection';
import InteractiveCard from './components/InteractiveCard';
import MorphingText from './components/MorphingText';
import ParticleField from './components/ParticleField';
import MagneticCursor from './components/MagneticCursor';
import GeographicJourney from './components/GeographicJourney';
import './App.css';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

function App() {
  useEffect(() => {
    // Initialize smooth scrolling and performance optimizations
    const initializeApp = () => {
      // Disable right-click context menu for a more immersive experience
      document.addEventListener('contextmenu', (e) => e.preventDefault());
      
      // Add performance monitoring
      if (process.env.NODE_ENV !== 'production') {
        let frameCount = 0;
        let lastTime = performance.now();
        
        const checkPerformance = () => {
          const now = performance.now();
          frameCount++;
          
          if (now >= lastTime + 1000) {
            const fps = frameCount;
            frameCount = 0;
            lastTime = now;
            
            if (fps < 45) {
              console.warn(`Performance alert: ${fps}fps - below target`);
            }
          }
          
          requestAnimationFrame(checkPerformance);
        };
        
        requestAnimationFrame(checkPerformance);
      }
    };

    initializeApp();

    return () => {
      document.removeEventListener('contextmenu', (e) => e.preventDefault());
    };
  }, []);

  return (
    <SmoothScroll>
      <div className="App">
        {/* Custom Cursor */}
        <CustomCursor />
        
        {/* Interactive Particle Background */}
        <ParticleField 
          particleCount={80}
          connectionDistance={120}
          mouseInfluence={150}
          colors={['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd']}
        />
        
        {/* Scroll Progress */}
        <ScrollProgress />
        
        {/* Floating Navigation */}
        <FloatingNavigation />
        
        {/* Main Content */}
        <main className="relative">
          {/* Hero Section */}
          <HeroSection />
          
          {/* Morphing Introduction Section */}
          <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
            <div className="container mx-auto px-6 text-center relative z-10">
              <MorphingText 
                texts={[
                  "Ethical Data Innovation",
                  "EU Data Sovereignty", 
                  "Democratic AI Governance",
                  "Human-Centric Design"
                ]}
                className="text-4xl md:text-6xl font-light text-slate-800 mb-8 lambda"
                interval={2500}
                morphDuration={800}
              />
              <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
                LUKHΛS represents a paradigm shift in artificial intelligence development, 
                prioritizing European values in the age of ΛGI.
              </p>
            </div>
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-slate-100/50"></div>
          </section>
          
          {/* Geographic Journey Section */}
          <GeographicJourney />
          
          {/* Horizontal Scrolling Systems Section */}
          <HorizontalScrollSection id="systems">
            <InteractiveCard
              title="ΛGI System"
              content="Our ΛGI architecture embodies the principles of transparency, accountability, and human-centric design, ensuring that artificial general intelligence serves humanity's best interests."
              icon="Λ"
              color="blue"
              size="large"
              animationType="float"
            />
            <InteractiveCard
              title="ΛiD System"
              content="The ΛiD (Lambda Identity) system provides secure, privacy-preserving identity management that respects individual autonomy while enabling seamless interaction with ΛGI systems."
              icon="🔐"
              color="purple"
              size="normal"
              animationType="pulse"
            />
            <InteractiveCard
              title="Data Sovereignty"
              content="European data remains under European control, ensuring compliance with GDPR and fostering trust in AI systems through transparent data governance."
              icon="🛡️"
              color="green"
              size="normal"
              animationType="rotate"
            />
            <InteractiveCard
              title="Rural Innovation"
              content="From the vineyards of Cuartillos, Jerez de la Frontera, to the corridors of Brussels, LUKHΛS bridges rural and urban communities."
              icon="🌾"
              color="orange"
              size="large"
              animationType="float"
            />
          </HorizontalScrollSection>
          
          {/* Enhanced Project Section with Magnetic Effects */}
          <section className="min-h-screen flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-slate-50 to-blue-50">
            <div className="container mx-auto px-6 text-center relative z-10">
              <MagneticCursor strength={0.2}>
                <h2 className="text-4xl md:text-6xl font-light text-slate-800 mb-8 lambda">
                  The Project
                </h2>
              </MagneticCursor>
              
              <div className="grid md:grid-cols-3 gap-8 mt-16">
                <MagneticCursor strength={0.15} className="group">
                  <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-xl p-6 h-64 flex flex-col justify-center items-center text-center transition-all duration-300 group-hover:bg-white/30">
                    <div className="text-3xl mb-4">🎯</div>
                    <h3 className="text-xl font-light text-slate-800 mb-2 lambda">Mission</h3>
                    <p className="text-slate-600">Ethical AI development for European sovereignty</p>
                  </div>
                </MagneticCursor>
                
                <MagneticCursor strength={0.15} className="group">
                  <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-xl p-6 h-64 flex flex-col justify-center items-center text-center transition-all duration-300 group-hover:bg-white/30">
                    <div className="text-3xl mb-4">🌍</div>
                    <h3 className="text-xl font-light text-slate-800 mb-2 lambda">Vision</h3>
                    <p className="text-slate-600">Global AI leadership through European values</p>
                  </div>
                </MagneticCursor>
                
                <MagneticCursor strength={0.15} className="group">
                  <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-xl p-6 h-64 flex flex-col justify-center items-center text-center transition-all duration-300 group-hover:bg-white/30">
                    <div className="text-3xl mb-4">⚡</div>
                    <h3 className="text-xl font-light text-slate-800 mb-2 lambda">Impact</h3>
                    <p className="text-slate-600">Transforming rural communities through AI</p>
                  </div>
                </MagneticCursor>
              </div>
            </div>
          </section>
          
          {/* Visuals Section with Different Animation */}
          <EnhancedSection
            id="visuals"
            title="Research & Visuals"
            content="Explore the data visualizations, research findings, and technical documentation that demonstrate LUKHΛS's capabilities and impact on European AI development."
            background="gradient"
            parallax={true}
            titleDelay={0.1}
            contentDelay={0.4}
          />
          
          {/* Contact Section with Enhanced Interactivity */}
          <section id="contact" className="min-h-screen flex items-center justify-center relative overflow-hidden">
            <div className="container mx-auto px-6 text-center relative z-10">
              <MagneticCursor strength={0.3}>
                <h2 className="text-4xl md:text-6xl font-light text-slate-800 mb-8 lambda">
                  Contact
                </h2>
              </MagneticCursor>
              <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed mb-12">
                Join us in shaping the future of ethical artificial intelligence.
              </p>
              
              {/* Enhanced Related Website Links */}
              <div className="flex justify-center space-x-16 mt-16">
                <MagneticCursor strength={0.4}>
                  <a 
                    href="https://www.lukhas.es" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="group relative block"
                    data-cursor="pointer"
                  >
                    <div className="text-3xl font-extralight text-slate-600 hover:text-blue-600 transition-all duration-500 transform group-hover:scale-125 interactive-element lambda">
                      ΛnD
                    </div>
                    <div className="absolute -bottom-3 left-0 w-0 h-1 bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-500 group-hover:w-full"></div>
                    <div className="absolute -top-2 -left-2 -right-2 -bottom-2 border border-blue-600/0 rounded-lg transition-all duration-300 group-hover:border-blue-600/30"></div>
                  </a>
                </MagneticCursor>
                
                <MagneticCursor strength={0.4}>
                  <a 
                    href="https://www.lukhas.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="group relative block"
                    data-cursor="pointer"
                  >
                    <div className="text-3xl font-extralight text-slate-600 hover:text-blue-600 transition-all duration-500 transform group-hover:scale-125 interactive-element lambda">
                      ΛGI
                    </div>
                    <div className="absolute -bottom-3 left-0 w-0 h-1 bg-gradient-to-r from-blue-600 to-green-600 transition-all duration-500 group-hover:w-full"></div>
                    <div className="absolute -top-2 -left-2 -right-2 -bottom-2 border border-blue-600/0 rounded-lg transition-all duration-300 group-hover:border-blue-600/30"></div>
                  </a>
                </MagneticCursor>
                
                <MagneticCursor strength={0.4}>
                  <a 
                    href="https://www.lukhas.id" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="group relative block"
                    data-cursor="pointer"
                  >
                    <div className="text-3xl font-extralight text-slate-600 hover:text-blue-600 transition-all duration-500 transform group-hover:scale-125 interactive-element lambda">
                      ΛiD
                    </div>
                    <div className="absolute -bottom-3 left-0 w-0 h-1 bg-gradient-to-r from-blue-600 to-orange-600 transition-all duration-500 group-hover:w-full"></div>
                    <div className="absolute -top-2 -left-2 -right-2 -bottom-2 border border-blue-600/0 rounded-lg transition-all duration-300 group-hover:border-blue-600/30"></div>
                  </a>
                </MagneticCursor>
              </div>
            </div>
            
            {/* Background decoration */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-purple-50/30"></div>
          </section>
        </main>
      </div>
    </SmoothScroll>
  );
}

export default App;
