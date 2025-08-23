import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import TextReveal from './TextReveal';

const EnhancedSection = ({ 
  id, 
  title, 
  content, 
  background = 'transparent',
  titleDelay = 0,
  contentDelay = 0.3,
  parallax = false 
}) => {
  const sectionRef = useRef(null);
  const backgroundRef = useRef(null);

  useEffect(() => {
    const section = sectionRef.current;
    const bg = backgroundRef.current;
    
    if (!section) return;

    // Parallax effect for background
    if (parallax && bg) {
      gsap.to(bg, {
        yPercent: -50,
        ease: 'none',
        scrollTrigger: {
          trigger: section,
          start: 'top bottom',
          end: 'bottom top',
          scrub: true
        }
      });
    }

    // Section entrance animation
    gsap.fromTo(section, 
      { opacity: 0 },
      {
        opacity: 1,
        duration: 1,
        scrollTrigger: {
          trigger: section,
          start: 'top 90%',
          toggleActions: 'play none none reverse'
        }
      }
    );

    return () => {
      ScrollTrigger.getAll().forEach(trigger => {
        if (trigger.trigger === section || trigger.trigger === bg) {
          trigger.kill();
        }
      });
    };
  }, [parallax]);

  const backgroundClass = background === 'glass' 
    ? 'bg-white/50 backdrop-blur-sm' 
    : background === 'gradient'
    ? 'gradient-overlay'
    : '';

  return (
    <section 
      ref={sectionRef}
      id={id} 
      className={`min-h-screen flex items-center justify-center relative overflow-hidden ${backgroundClass}`}
    >
      {/* Background Element for Parallax */}
      {parallax && (
        <div 
          ref={backgroundRef}
          className="absolute inset-0 w-full h-[120%] -z-10"
          style={{
            background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(59, 130, 246, 0.02) 50%, rgba(147, 197, 253, 0.05) 100%)'
          }}
        />
      )}

      <div className="container mx-auto px-6 text-center relative z-10">
        {/* Title with Text Reveal */}
        <TextReveal 
          className="text-4xl md:text-6xl font-light text-slate-800 mb-8 lambda"
          delay={titleDelay}
          stagger={0.03}
        >
          {title}
        </TextReveal>

        {/* Content with Text Reveal */}
        <TextReveal 
          className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed"
          delay={contentDelay}
          stagger={0.01}
        >
          {content}
        </TextReveal>
      </div>

      {/* Decorative Elements */}
      <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/20 rounded-full animate-pulse" />
      <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-blue-500/30 rounded-full animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-2/3 left-1/6 w-1.5 h-1.5 bg-blue-300/25 rounded-full animate-pulse" style={{ animationDelay: '2s' }} />
    </section>
  );
};

export default EnhancedSection;

