'use client';

import { useEffect, useRef } from 'react';
import Lenis from 'lenis';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP plugins
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

interface SmoothScrollProps {
  children: React.ReactNode;
}

export default function SmoothScroll({ children }: SmoothScrollProps) {
  const lenisRef = useRef<Lenis | null>(null);

  useEffect(() => {
    // Initialize Lenis smooth scroll
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    });

    lenisRef.current = lenis;

    // Connect Lenis to GSAP ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);

    gsap.ticker.add((time) => {
      lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);

    // Consciousness-aware scroll animations
    const initScrollAnimations = () => {
      // Reveal animations for sections
      gsap.utils.toArray('.reveal-section').forEach((section: any) => {
        gsap.fromTo(section, 
          {
            y: 100,
            opacity: 0,
            scale: 0.95,
          },
          {
            y: 0,
            opacity: 1,
            scale: 1,
            duration: 1.2,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 85%',
              end: 'bottom 15%',
              toggleActions: 'play none none reverse',
            }
          }
        );
      });

      // Stagger animations for cards and items
      gsap.utils.toArray('.reveal-stagger').forEach((container: any) => {
        const items = container.querySelectorAll('.reveal-item');
        
        gsap.fromTo(items,
          {
            y: 60,
            opacity: 0,
          },
          {
            y: 0,
            opacity: 1,
            duration: 0.8,
            stagger: 0.1,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: container,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            }
          }
        );
      });

      // Consciousness pulse effect for interactive elements
      gsap.utils.toArray('.consciousness-pulse').forEach((element: any) => {
        const tl = gsap.timeline({ 
          repeat: -1, 
          yoyo: true,
          paused: true 
        });
        
        tl.to(element, {
          scale: 1.05,
          duration: 2,
          ease: 'sine.inOut',
        });

        ScrollTrigger.create({
          trigger: element,
          start: 'top 80%',
          end: 'bottom 20%',
          onEnter: () => tl.play(),
          onLeave: () => tl.pause(),
          onEnterBack: () => tl.play(),
          onLeaveBack: () => tl.pause(),
        });
      });

      // Neural network lines animation
      gsap.utils.toArray('.neural-line').forEach((line: any) => {
        gsap.fromTo(line,
          {
            scaleX: 0,
            transformOrigin: 'left center',
          },
          {
            scaleX: 1,
            duration: 1.5,
            ease: 'power2.inOut',
            scrollTrigger: {
              trigger: line,
              start: 'top 75%',
              toggleActions: 'play none none reverse',
            }
          }
        );
      });

      // Consciousness field intensity based on scroll
      ScrollTrigger.create({
        trigger: 'body',
        start: 'top top',
        end: 'bottom bottom',
        onUpdate: (self) => {
          const intensity = 1 + self.progress * 0.5;
          document.documentElement.style.setProperty('--consciousness-intensity', intensity.toString());
        }
      });

      // Parallax effects for background elements
      gsap.utils.toArray('.parallax').forEach((element: any) => {
        const speed = element.dataset.speed || 0.5;
        
        gsap.to(element, {
          y: () => -window.innerHeight * parseFloat(speed),
          ease: 'none',
          scrollTrigger: {
            trigger: element,
            start: 'top bottom',
            end: 'bottom top',
            scrub: 1,
          }
        });
      });

      // Text reveal animations
      gsap.utils.toArray('.text-reveal').forEach((text: any) => {
        const chars = text.textContent.split('');
        text.innerHTML = chars.map((char: string) => 
          char === ' ' ? ' ' : `<span class="char">${char}</span>`
        ).join('');

        const charElements = text.querySelectorAll('.char');
        
        gsap.fromTo(charElements,
          {
            y: 30,
            opacity: 0,
          },
          {
            y: 0,
            opacity: 1,
            duration: 0.5,
            stagger: 0.02,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: text,
              start: 'top 80%',
              toggleActions: 'play none none reverse',
            }
          }
        );
      });
    };

    // Initialize animations when DOM is ready
    const initTimer = setTimeout(initScrollAnimations, 100);

    return () => {
      clearTimeout(initTimer);
      lenis.destroy();
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
      gsap.ticker.remove(lenis.raf);
    };
  }, []);

  return (
    <div className="lenis-scroll-container">
      {children}
      
      <style jsx global>{`
        html.lenis, html.lenis body {
          height: auto;
        }
        
        .lenis.lenis-smooth {
          scroll-behavior: auto !important;
        }
        
        .lenis.lenis-smooth [data-lenis-prevent] {
          overscroll-behavior: contain;
        }
        
        .char {
          display: inline-block;
        }
        
        .reveal-section {
          will-change: transform, opacity;
        }
        
        .reveal-item {
          will-change: transform, opacity;
        }
        
        .consciousness-pulse {
          will-change: transform;
        }
        
        .neural-line {
          will-change: transform;
        }
        
        .parallax {
          will-change: transform;
        }
      `}</style>
    </div>
  );
}