import { useEffect, useRef } from 'react';

const CustomCursor = () => {
  const cursorRef = useRef(null);
  const mousePos = useRef({ x: 0, y: 0 });
  const cursorPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const cursor = cursorRef.current;
    if (!cursor) return;

    let animationId;

    // Mouse move handler
    const handleMouseMove = (e) => {
      mousePos.current.x = e.clientX;
      mousePos.current.y = e.clientY;
    };

    // Smooth cursor animation
    const animateCursor = () => {
      const speed = 0.12;
      
      cursorPos.current.x += (mousePos.current.x - cursorPos.current.x) * speed;
      cursorPos.current.y += (mousePos.current.y - cursorPos.current.y) * speed;
      
      cursor.style.transform = `translate3d(${cursorPos.current.x}px, ${cursorPos.current.y}px, 0)`;
      
      animationId = requestAnimationFrame(animateCursor);
    };

    // Interactive element handlers
    const handleMouseEnter = (e) => {
      const target = e.target;
      
      if (target.matches('a, button, [data-cursor="pointer"]')) {
        cursor.classList.add('hover');
      } else if (target.matches('p, h1, h2, h3, h4, h5, h6, span')) {
        cursor.classList.add('text');
      }
    };

    const handleMouseLeave = () => {
      cursor.classList.remove('hover', 'text');
    };

    // Event listeners
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseenter', handleMouseEnter, true);
    document.addEventListener('mouseleave', handleMouseLeave, true);
    
    // Start animation
    animateCursor();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseenter', handleMouseEnter, true);
      document.removeEventListener('mouseleave', handleMouseLeave, true);
      
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, []);

  return <div ref={cursorRef} className="custom-cursor" />;
};

export default CustomCursor;

