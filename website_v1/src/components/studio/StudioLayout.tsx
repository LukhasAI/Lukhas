'use client';

import { useEffect } from 'react';

interface StudioLayoutProps {
  children: React.ReactNode;
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  fullscreen: boolean;
}

export default function StudioLayout({
  children,
  leftCollapsed,
  rightCollapsed,
  fullscreen,
}: StudioLayoutProps) {
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Space = fullscreen, Cmd/Ctrl+K = palette, [ and ] = toggles (parent handles)
      if (e.code === 'Space' && e.target === document.body) e.preventDefault();
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') e.preventDefault();
      if ((e.metaKey || e.ctrlKey) && (e.key === '[' || e.key === ']')) e.preventDefault();
    };
    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, []);

  // >>> New: inline grid template (Tailwind can't generate runtime arbitrary classes)
  const gridTemplateColumns = fullscreen
    ? '0px 1fr 0px'
    : `${leftCollapsed ? '12px' : '208px'} 1fr ${rightCollapsed ? '12px' : '232px'}`;

  // >>> New: remove horizontal gap when any bar is collapsed or in fullscreen
  const columnGap = fullscreen ? '0px' : '8px';

  return (
    <div className="h-screen bg-[var(--background)] text-[var(--text-primary)] overflow-hidden">
      <div
        className={`
          h-full grid grid-rows-[1fr_auto] transition-all duration-300 ease-in-out
        `}
        style={{
          gridTemplateAreas: `
            "left context right"
            "left chat right"
          `,
          gridTemplateColumns,
          columnGap,
        }}
      >
        {children}
      </div>
    </div>
  );
}