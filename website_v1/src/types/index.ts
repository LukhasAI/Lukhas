export interface Product {
  name: string;
  desc: string;
  href: string;
}

export interface SocialLink {
  name: string;
  icon: string;
  href: string;
}

export interface NavLink {
  label: string;
  href: string;
}

export type Theme = 'dark' | 'light';
export type GlassOverlay = boolean;

export interface ThemeContextType {
  theme: Theme;
  glassOverlay: GlassOverlay;
  setTheme: (theme: Theme) => void;
  toggleGlassOverlay: () => void;
}

export type StudioLayoutPreset = 'default' | 'email_focused' | 'builder_mode';

export type ContextAreaState = 'canvas' | 'preview' | 'player' | 'dashboard' | 'browser';

export type ChatMode = 'chat' | 'code' | 'email' | 'command';

export type SendTarget = 'agent' | 'email' | 'sms' | 'document' | 'notes';

export interface StudioState {
  leftSidebarExpanded: boolean;
  rightSidebarExpanded: boolean;
  contextAreaState: ContextAreaState;
  chatMode: ChatMode;
  isFullscreen: boolean;
  preset: StudioLayoutPreset;
}

export interface QuickIcon {
  id: string;
  tooltip: string;
  icon?: React.ComponentType;
}

export interface MessageBubble {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  actions?: string[];
}

export interface Widget {
  id: string;
  name: string;
  component: React.ComponentType;
  position: 'left' | 'right';
}