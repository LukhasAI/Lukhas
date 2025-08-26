import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';

const MorphingText = ({
  texts = [],
  className = '',
  interval = 3000,
  morphDuration = 1000
}) => {
  const textRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (texts.length <= 1) return;

    const element = textRef.current;
    if (!element) return;

    const morphText = () => {
      const currentText = texts[currentIndex];
      const nextIndex = (currentIndex + 1) % texts.length;
      const nextText = texts[nextIndex];

      // Split current text into characters
      const currentChars = currentText.split('');
      const nextChars = nextText.split('');
      const maxLength = Math.max(currentChars.length, nextChars.length);

      // Clear element and create character spans
      element.innerHTML = '';

      for (let i = 0; i < maxLength; i++) {
        const span = document.createElement('span');
        span.className = 'char inline-block';
        span.textContent = currentChars[i] || '';
        span.style.opacity = currentChars[i] ? '1' : '0';
        element.appendChild(span);
      }

      const chars = element.querySelectorAll('.char');

      // Animate out current characters
      gsap.to(chars, {
        y: -50,
        opacity: 0,
        rotateX: -90,
        duration: morphDuration / 2000,
        stagger: 0.02,
        ease: 'power2.in',
        onComplete: () => {
          // Update characters to next text
          chars.forEach((char, i) => {
            char.textContent = nextChars[i] || '';
            if (nextChars[i]) {
              gsap.set(char, { y: 50, opacity: 0, rotateX: 90 });
            }
          });

          // Animate in new characters
          gsap.to(chars, {
            y: 0,
            opacity: (i) => nextChars[i] ? 1 : 0,
            rotateX: 0,
            duration: morphDuration / 2000,
            stagger: 0.02,
            ease: 'power2.out',
          });

          setCurrentIndex(nextIndex);
        }
      });
    };

    const intervalId = setInterval(morphText, interval);

    return () => clearInterval(intervalId);
  }, [texts, currentIndex, interval, morphDuration]);

  if (texts.length === 0) return null;

  return (
    <div
      ref={textRef}
      className={`morphing-text ${className}`}
      style={{
        transformStyle: 'preserve-3d',
        perspective: '1000px'
      }}
    >
      {texts[currentIndex]}
    </div>
  );
};

export default MorphingText;
