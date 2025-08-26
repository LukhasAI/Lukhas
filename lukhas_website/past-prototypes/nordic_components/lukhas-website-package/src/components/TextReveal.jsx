import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

const TextReveal = ({ children, className = '', delay = 0, stagger = 0.02 }) => {
  const textRef = useRef(null);

  useEffect(() => {
    const element = textRef.current;
    if (!element) return;

    // Split text into characters for animation
    const text = element.textContent;
    const chars = text.split('').map((char, index) => {
      const span = document.createElement('span');
      span.textContent = char === ' ' ? '\u00A0' : char; // Non-breaking space
      span.className = 'char';
      span.style.display = 'inline-block';
      span.style.transform = 'translateY(100%) rotateX(-90deg)';
      span.style.opacity = '0';
      return span;
    });

    // Clear original text and add character spans
    element.innerHTML = '';
    chars.forEach(char => element.appendChild(char));

    // Create animation timeline
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: element,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      }
    });

    // Animate characters
    tl.to(chars, {
      opacity: 1,
      y: 0,
      rotateX: 0,
      duration: 0.8,
      stagger: stagger,
      ease: 'back.out(1.7)',
      delay: delay
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => {
        if (trigger.trigger === element) {
          trigger.kill();
        }
      });
    };
  }, [delay, stagger]);

  return (
    <div ref={textRef} className={`text-reveal ${className}`}>
      {children}
    </div>
  );
};

export default TextReveal;
