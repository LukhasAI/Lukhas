import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';

const HeroSection = () => {
  const heroRef = useRef(null);
  const logoRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);

  useEffect(() => {
    const hero = heroRef.current;
    const logo = logoRef.current;
    const title = titleRef.current;
    const subtitle = subtitleRef.current;

    if (!hero || !logo || !title || !subtitle) return;

    // Set initial states
    gsap.set([logo, title, subtitle], {
      opacity: 0,
      y: 50,
    });

    // Create entrance animation timeline
    const tl = gsap.timeline({ delay: 0.5 });

    tl.to(logo, {
      opacity: 1,
      y: 0,
      duration: 1.2,
      ease: 'power3.out',
    })
    .to(title, {
      opacity: 1,
      y: 0,
      duration: 1,
      ease: 'power3.out',
    }, '-=0.8')
    .to(subtitle, {
      opacity: 1,
      y: 0,
      duration: 0.8,
      ease: 'power3.out',
    }, '-=0.6');

    // Parallax effect on scroll
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const parallaxSpeed = 0.5;
      
      gsap.set(hero, {
        y: scrollY * parallaxSpeed,
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      tl.kill();
    };
  }, []);

  return (
    <section ref={heroRef} className="hero-section">
      <div className="text-center z-10 relative">
        {/* Lambda Logo */}
        <div ref={logoRef} className="mb-8">
          <div className="lambda text-9xl md:text-[12rem] text-blue-600 mb-4">
            Λ
          </div>
        </div>

        {/* Company Name */}
        <h1 ref={titleRef} className="text-hero lambda text-slate-800 mb-6">
          LUKHΛS
        </h1>

        {/* Subtitle */}
        <p ref={subtitleRef} className="text-subtitle text-slate-600 max-w-2xl mx-auto px-6">
          Ethical data innovation & EU Data Sovereignty
        </p>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-6 h-10 border-2 border-slate-400 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-slate-400 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 gradient-overlay pointer-events-none"></div>
    </section>
  );
};

export default HeroSection;

