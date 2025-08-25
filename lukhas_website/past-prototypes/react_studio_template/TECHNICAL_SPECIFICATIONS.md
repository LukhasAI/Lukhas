# LUKHΛS Studio V-2 Technical Specifications

## 🏗 Architecture Overview

### Component Hierarchy
```
App_Clean.jsx
├── AnimatedBackground (dynamic import)
├── CommandPalette (modal overlay)
├── LeftDock
│   ├── SettingsButton (hamburger menu)
│   ├── LUKHΛS Brand
│   ├── TextTools (conditional)
│   ├── CoreApplications (grid)
│   ├── LUKHΛS Modules (compact grid)
│   └── Conversations (scrollable list)
├── DesktopArea
│   ├── DragDropZone
│   └── DesktopItems (positioned absolutely)
├── RightDock
│   ├── AgentSelector (interactive)
│   ├── QuickAgentSwitcher
│   ├── AdditionalTools
│   └── SystemStatus
├── FloatingChatInterface
│   ├── ChatInput (with emoji picker)
│   ├── SendButton
│   ├── ModeSelector (chat/code/text/creative)
│   └── ActionControls (add/attach/share)
└── SettingsPanel (modal overlay)
```

### State Architecture
```javascript
// Core UI State
const [commandPaletteVisible, setCommandPaletteVisible] = useState(false)
const [commandPaletteLevel, setCommandPaletteLevel] = useState(0)
const [showLeftDock, setShowLeftDock] = useState(true)
const [showRightDock, setShowRightDock] = useState(true)
const [showSettings, setShowSettings] = useState(false)

// Chat State
const [chatMessage, setChatMessage] = useState('')
const [chatMode, setChatMode] = useState('chat')
const [showTextTools, setShowTextTools] = useState(false)
const [showSendOptions, setShowSendOptions] = useState(false)

// Customization State
const [animatedBg, setAnimatedBg] = useState('constellation')
const [bgColor, setBgColor] = useState('#1a1a2e')
const [customBgImage, setCustomBgImage] = useState(null)

// Desktop State
const [desktopItems, setDesktopItems] = useState([])
const [dragOverDesktop, setDragOverDesktop] = useState(false)
const [selectedAgent, setSelectedAgent] = useState('OpenAI O1')
```

## 🎨 Design System Specifications

### Color System
```css
/* Primary Palette */
--slate-50: #f8fafc;
--slate-100: #f1f5f9;
--slate-200: #e2e8f0;
--slate-300: #cbd5e1;
--slate-400: #94a3b8;
--slate-500: #64748b;
--slate-600: #475569;
--slate-700: #334155;
--slate-800: #1e293b;
--slate-900: #0f172a;

/* Background Gradients */
--bg-primary: linear-gradient(to bottom right, #111827, #000000);
--bg-dock: rgba(31, 41, 55, 0.3);
--bg-chat: rgba(31, 41, 55, 0.9);

/* Shadows */
--shadow-3d: 0 25px 50px -12px rgba(0, 0, 0, 0.5),
             0 8px 16px -8px rgba(0, 0, 0, 0.3),
             inset 0 1px 0 rgba(255, 255, 255, 0.1);
```

### Typography Scale
```css
/* Font Families */
--font-primary: 'Helvetica Neue', -apple-system, system-ui, sans-serif;

/* Font Weights */
--font-thin: 100;
--font-light: 300;
--font-medium: 500;

/* Text Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
```

### Layout Specifications
```css
/* Dock Dimensions */
--dock-left-width: 14rem;    /* 224px */
--dock-right-width: 12rem;   /* 192px */
--dock-padding: 1rem;        /* 16px */

/* Chat Interface */
--chat-bottom-offset: 1.5rem; /* 24px */
--chat-border-radius: 1.5rem; /* 24px */
--chat-padding: 1rem;        /* 16px */
--chat-input-height: 3rem;   /* 48px */

/* Desktop */
--desktop-padding: 1.5rem;   /* 24px */
--desktop-border-radius: 1.5rem; /* 24px */
```

## 🔧 Component Specifications

### AnimatedBackground.jsx
```javascript
// Props Interface
interface AnimatedBackgroundProps {
  type: 'constellation' | 'clouds' | 'custom' | 'color';
  isActive: boolean;
  customImage?: string;
  color?: string;
}

// Performance Optimizations
- RequestAnimationFrame for smooth animations
- Cleanup on unmount to prevent memory leaks
- Conditional rendering based on isActive prop
- GPU acceleration with transform3d
```

### FloatingChatInterface
```javascript
// Positioning Logic
const positioning = {
  left: showLeftDock ? '15rem' : '1.5rem',
  right: showRightDock ? '13rem' : '1.5rem',
  bottom: '1.5rem',
  transition: 'left 300ms, right 300ms'
}

// Icon Organization
const leftIcons = [
  { id: 'chat', icon: MessageSquare, tooltip: 'Chat' },
  { id: 'code', icon: Code, tooltip: 'Code' },
  { id: 'text', icon: Edit, tooltip: 'Text' },
  { id: 'creative', icon: Star, tooltip: 'Creative' }
]

const rightIcons = [
  { icon: Plus, action: 'showAddItems', tooltip: 'Add items' },
  { icon: Paperclip, action: 'attach', tooltip: 'Attach' },
  { icon: Share, action: 'share', tooltip: 'Share to agents' }
]
```

### CommandPalette
```javascript
// Two-Level Interface
Level 1: Quick Commands (search)
- Settings & Preferences
- Open Code Editor  
- Open Terminal
- New Document
- Find in Files
- Switch AI Model
- New Chat Session

Level 2: Detailed Settings (expanded)
- Background Settings (4 options)
- Interface Controls (dock visibility)
- Accessibility Options
- AI Settings
```

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }

/* Dock Behavior */
Mobile (< 768px): Docks collapse to overlay mode
Tablet (768px - 1024px): Reduced dock widths
Desktop (> 1024px): Full dock widths
```

## 🔌 Integration Points

### Backend API Requirements
```javascript
// Chat Endpoints
POST /api/chat/message
GET /api/chat/history
DELETE /api/chat/session

// Agent Management
GET /api/agents/available
POST /api/agents/switch
GET /api/agents/status

// File Management  
POST /api/files/upload
GET /api/files/list
DELETE /api/files/:id

// User Preferences
GET /api/user/settings
PUT /api/user/settings
```

### WebSocket Events
```javascript
// Incoming Events
'message_received'    // New AI response
'agent_status_change' // Agent online/offline
'file_upload_complete' // File processing done
'typing_indicator'    // Agent is processing

// Outgoing Events  
'send_message'        // User message
'switch_agent'        // Change active agent
'upload_file'         // File attachment
'join_session'        // Enter chat session
```

### LocalStorage Schema
```javascript
// User Preferences
localStorage.setItem('lukhas_preferences', JSON.stringify({
  theme: {
    background: 'constellation',
    color: '#1a1a2e',
    customImage: null
  },
  layout: {
    showLeftDock: true,
    showRightDock: true,
    dockPositions: { left: 224, right: 192 }
  },
  chat: {
    selectedAgent: 'OpenAI O1',
    defaultMode: 'chat',
    messageHistory: []
  }
}))
```

## 🚀 Performance Metrics

### Target Performance
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Bundle Size: < 500KB (gzipped)

### Optimization Strategies
- Code Splitting: Dynamic imports for backgrounds
- Tree Shaking: Remove unused dependencies
- Image Optimization: WebP format with fallbacks
- Caching: Service worker for static assets

## 🔒 Security Considerations

### Content Security Policy
```
default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:;
connect-src 'self' wss: https:;
```

### Input Sanitization
- XSS Protection: Sanitize all user inputs
- File Upload: Validate file types and sizes  
- CSRF Protection: Token-based validation
- Rate Limiting: API request throttling

## 📊 Monitoring & Analytics

### Performance Monitoring
```javascript
// Custom Performance Hook
const performanceMetrics = {
  renderTime: Date.now() - startTime,
  memoryUsage: performance.memory?.usedJSHeapSize,
  animationFPS: frameCount / timeElapsed,
  errorCount: errorLog.length
}
```

### User Analytics
- Feature Usage: Track most used components
- Performance Data: Client-side metrics
- Error Tracking: Automatic error reporting
- A/B Testing: Component variant testing

---

**Technical Specification Version**: 2.0  
**Last Updated**: June 27, 2025  
**Maintained by**: LUKHΛS AI Development Team
