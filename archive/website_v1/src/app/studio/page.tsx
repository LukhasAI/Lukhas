'use client';

import { useState } from 'react';
import StudioLayout from '@/components/studio/StudioLayout';
import LeftSidebar from '@/components/studio/LeftSidebar';
import ContextArea from '@/components/studio/ContextArea';
import RightSidebar from '@/components/studio/RightSidebar';
import ChatInterface from '@/components/studio/ChatInterface';

export default function StudioPage() {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [contextState, setContextState] = useState<'canvas' | 'preview' | 'player' | 'dashboard' | 'browser'>('canvas');

  return (
    <StudioLayout
      leftCollapsed={leftCollapsed}
      rightCollapsed={rightCollapsed}
      fullscreen={fullscreen}
    >
      <LeftSidebar 
        collapsed={leftCollapsed}
        onToggle={() => setLeftCollapsed(!leftCollapsed)}
        contextState={contextState}
      />
      
      <ContextArea 
        state={contextState}
        onStateChange={setContextState}
        fullscreen={fullscreen}
        onFullscreenChange={setFullscreen}
      />
      
      <RightSidebar 
        collapsed={rightCollapsed}
        onToggle={() => setRightCollapsed(!rightCollapsed)}
        contextState={contextState}
      />
      
      <ChatInterface 
        fullscreen={fullscreen}
        contextState={contextState}
      />
    </StudioLayout>
  );
}