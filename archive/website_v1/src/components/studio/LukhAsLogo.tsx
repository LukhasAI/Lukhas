'use client';

import { useState } from 'react';

interface LukhAsLogoProps {
  size?: number;
  className?: string;
  interactive?: boolean;
  onClick?: () => void;
}

export default function LukhAsLogo({ 
  size = 24, 
  className = '', 
  interactive = false,
  onClick 
}: LukhAsLogoProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={`inline-flex items-center gap-2 ${interactive ? 'cursor-pointer' : ''} ${className}`}
      onMouseEnter={() => interactive && setIsHovered(true)}
      onMouseLeave={() => interactive && setIsHovered(false)}
      onClick={onClick}
    >
      {/* Sophisticated Lambda Symbol */}
      <div 
        className={`relative flex items-center justify-center transition-all duration-300 ${
          interactive && isHovered ? 'scale-110' : ''
        }`}
        style={{ width: size, height: size }}
      >
        {/* Outer glow effect when hovered */}
        {interactive && isHovered && (
          <div 
            className="absolute inset-0 bg-accent/20 rounded-full blur-md"
            style={{ width: size * 1.5, height: size * 1.5, left: -size * 0.25, top: -size * 0.25 }}
          />
        )}
        
        {/* Main Lambda symbol with gradient */}
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="relative z-10"
        >
          <defs>
            <linearGradient id="lambdaGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={interactive && isHovered ? "#6B9EFF" : "#4F8BFF"} />
              <stop offset="100%" stopColor={interactive && isHovered ? "#FF8FA3" : "#4F8BFF"} />
            </linearGradient>
          </defs>
          
          {/* Lambda symbol path */}
          <path
            d="M3 21L9 3H11L17 21H15L13.5 16H8.5L7 21H3ZM9.5 12H12.5L11 7L9.5 12Z"
            fill="url(#lambdaGradient)"
            className={`transition-all duration-300 ${
              interactive && isHovered ? 'drop-shadow-lg' : ''
            }`}
          />
          
          {/* Accent dots for sophistication */}
          <circle cx="6" cy="4" r="1" fill="currentColor" opacity="0.3" />
          <circle cx="18" cy="20" r="1" fill="currentColor" opacity="0.3" />
        </svg>
      </div>

      {/* LUKHAS text with sophisticated typography */}
      <div className="flex items-baseline gap-0">
        <span className={`font-bold tracking-tight transition-all duration-300 ${
          interactive && isHovered ? 'text-accent' : 'text-[var(--text-primary)]'
        }`}>
          LUKH
        </span>
        <span className={`font-bold tracking-tight transition-all duration-300 ${
          interactive && isHovered ? 'text-accent scale-110' : 'text-accent'
        }`}>
          Λ
        </span>
        <span className={`font-bold tracking-tight transition-all duration-300 ${
          interactive && isHovered ? 'text-accent' : 'text-[var(--text-primary)]'
        }`}>
          S
        </span>
      </div>

      {/* Subtle consciousness indicator */}
      {interactive && (
        <div className="flex items-center ml-1">
          <div className={`w-1.5 h-1.5 rounded-full transition-all duration-500 ${
            isHovered ? 'bg-accent animate-pulse' : 'bg-[var(--text-secondary)] opacity-50'
          }`} />
        </div>
      )}
    </div>
  );
}