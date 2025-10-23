import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

const HorizontalScrollSection = ({ children, id }) => {
  const containerRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    const scrollContainer = scrollRef.current;
    
    if (!container || !scrollContainer) return;

    // Calculate scroll distance
    const scrollWidth = scrollContainer.scrollWidth - window.innerWidth;
    
    // Create horizontal scroll animation
    const horizontalScroll = gsap.to(scrollContainer, {
      x: -scrollWidth,
      ease: 'none',
      scrollTrigger: {
        trigger: container,
        start: 'top top',
        end: () => `+=${scrollWidth}`,
        scrub: 1,
        pin: true,
        anticipatePin: 1,
        invalidateOnRefresh: true,
      }
    });

    // Add entrance animations for cards
    const cards = scrollContainer.querySelectorAll('.horizontal-card');
    cards.forEach((card, index) => {
      gsap.fromTo(card, 
        { 
          opacity: 0, 
          y: 100,
          rotateY: -15,
          scale: 0.8
        },
        {
          opacity: 1,
          y: 0,
          rotateY: 0,
          scale: 1,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: card,
            start: 'left 80%',
            end: 'left 20%',
            containerAnimation: horizontalScroll,
            toggleActions: 'play none none reverse'
          }
        }
      );
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => {
        if (trigger.trigger === container || trigger.trigger?.closest('.horizontal-scroll')) {
          trigger.kill();
        }
      });
    };
  }, []);

  return (
    <section ref={containerRef} id={id} className="horizontal-scroll relative overflow-hidden">
      <div 
        ref={scrollRef} 
        className="flex items-center h-screen w-max"
        style={{ width: 'max-content' }}
      >
        {children}
      </div>
    </section>
  );
};

export default HorizontalScrollSection;

