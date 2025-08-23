import { useRef, useEffect } from 'react';
import { gsap } from 'gsap';

const InteractiveCard = ({ 
  title, 
  content, 
  icon, 
  color = 'blue',
  size = 'normal',
  animationType = 'float'
}) => {
  const cardRef = useRef(null);
  const contentRef = useRef(null);
  const glowRef = useRef(null);

  useEffect(() => {
    const card = cardRef.current;
    const content = contentRef.current;
    const glow = glowRef.current;
    
    if (!card) return;

    // Mouse move handler for 3D tilt effect
    const handleMouseMove = (e) => {
      const rect = card.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const deltaX = (e.clientX - centerX) / (rect.width / 2);
      const deltaY = (e.clientY - centerY) / (rect.height / 2);
      
      gsap.to(card, {
        rotateY: deltaX * 15,
        rotateX: -deltaY * 15,
        duration: 0.3,
        ease: 'power2.out',
        transformPerspective: 1000,
      });

      gsap.to(content, {
        x: deltaX * 10,
        y: deltaY * 10,
        duration: 0.3,
        ease: 'power2.out',
      });

      if (glow) {
        gsap.to(glow, {
          x: deltaX * 20,
          y: deltaY * 20,
          opacity: 0.6,
          duration: 0.3,
          ease: 'power2.out',
        });
      }
    };

    const handleMouseLeave = () => {
      gsap.to(card, {
        rotateY: 0,
        rotateX: 0,
        duration: 0.5,
        ease: 'power2.out',
      });

      gsap.to(content, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: 'power2.out',
      });

      if (glow) {
        gsap.to(glow, {
          x: 0,
          y: 0,
          opacity: 0,
          duration: 0.5,
          ease: 'power2.out',
        });
      }
    };

    // Different animation types
    if (animationType === 'float') {
      gsap.to(card, {
        y: -10,
        duration: 2,
        ease: 'power2.inOut',
        yoyo: true,
        repeat: -1,
      });
    } else if (animationType === 'pulse') {
      gsap.to(card, {
        scale: 1.05,
        duration: 1.5,
        ease: 'power2.inOut',
        yoyo: true,
        repeat: -1,
      });
    } else if (animationType === 'rotate') {
      gsap.to(card.querySelector('.card-icon'), {
        rotation: 360,
        duration: 8,
        ease: 'none',
        repeat: -1,
      });
    }

    card.addEventListener('mousemove', handleMouseMove);
    card.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      card.removeEventListener('mousemove', handleMouseMove);
      card.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [animationType]);

  const sizeClasses = {
    small: 'w-80 h-60',
    normal: 'w-96 h-80',
    large: 'w-[28rem] h-96'
  };

  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/30 border-blue-400/30',
    purple: 'from-purple-500/20 to-purple-600/30 border-purple-400/30',
    green: 'from-green-500/20 to-green-600/30 border-green-400/30',
    orange: 'from-orange-500/20 to-orange-600/30 border-orange-400/30'
  };

  return (
    <div className="horizontal-card relative mx-8 first:ml-16 last:mr-16">
      {/* Glow effect */}
      <div 
        ref={glowRef}
        className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} rounded-2xl blur-xl opacity-0 -z-10`}
      />
      
      {/* Main card */}
      <div
        ref={cardRef}
        className={`${sizeClasses[size]} bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 cursor-pointer transition-all duration-300 hover:bg-white/15 relative overflow-hidden`}
        data-cursor="pointer"
      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-4 right-4 w-32 h-32 bg-gradient-to-br from-white to-transparent rounded-full" />
          <div className="absolute bottom-4 left-4 w-24 h-24 bg-gradient-to-tr from-white to-transparent rounded-full" />
        </div>

        <div ref={contentRef} className="relative z-10 h-full flex flex-col">
          {/* Icon */}
          {icon && (
            <div className="card-icon text-4xl mb-6 text-slate-700">
              {icon}
            </div>
          )}

          {/* Title */}
          <h3 className="text-2xl font-light text-slate-800 mb-4 lambda">
            {title}
          </h3>

          {/* Content */}
          <p className="text-slate-600 leading-relaxed flex-1">
            {content}
          </p>

          {/* Decorative line */}
          <div className={`w-16 h-0.5 bg-gradient-to-r ${colorClasses[color]} mt-6`} />
        </div>
      </div>
    </div>
  );
};

export default InteractiveCard;

