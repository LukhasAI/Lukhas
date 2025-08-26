import { useState, useEffect, useRef } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Button } from './components/ui/button.jsx'
import { Input } from './components/ui/input.jsx'
import AnimatedBackground from './components/AnimatedBackground.jsx'
import {
  Settings,
  User,
  MessageSquare,
  Search,
  Home,
  FileText,
  Image,
  Video,
  Code,
  Database,
  Cloud,
  Zap,
  Star,
  Heart,
  Bookmark,
  Share,
  Download,
  Upload,
  Edit,
  Trash,
  Plus,
  Minus,
  X,
  Menu,
  ChevronDown,
  ChevronUp,
  Send,
  Paperclip,
  Smile,
  Bold,
  Italic,
  Underline,
  Link,
  List,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Save,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  Twitter,
  Mail,
  Cloud as CloudIcon,
  BarChart2
} from 'lucide-react'
import './App.css'

function App() {
  const [commandPaletteVisible, setCommandPaletteVisible] = useState(false)
  const [commandPaletteLevel, setCommandPaletteLevel] = useState(0) // 0: hidden, 1: half, 2: full
  const [chatMessage, setChatMessage] = useState('')
  const [showTextTools, setShowTextTools] = useState(false)
  const [showSendOptions, setShowSendOptions] = useState(false)
  const [keySequence, setKeySequence] = useState([])
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [animatedBg, setAnimatedBg] = useState('stars') // 'stars', 'geometric', 'clouds', 'constellation', 'color', 'custom'
  const [bgColor, setBgColor] = useState('#1a1a2e') // Solid color background option
  const [customBgImage, setCustomBgImage] = useState(null)
  const [showLeftDock, setShowLeftDock] = useState(true)
  const [showRightDock, setShowRightDock] = useState(true)
  const [showHeader, setShowHeader] = useState(false) // Initially hidden
  const [chatMode, setChatMode] = useState('chat') // 'chat', 'code', 'creative'
  const [desktopItems, setDesktopItems] = useState([]) // Items dropped on desktop
  const [dragOverDesktop, setDragOverDesktop] = useState(false)
  const [expandedStack, setExpandedStack] = useState(null)

  const sendButtonRef = useRef(null)

  // Show text tools only in code/editor mode
  useEffect(() => {
    setShowTextTools(chatMode === 'code')
  }, [chatMode])

  // Simplified keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Command palette: Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteVisible(!commandPaletteVisible)
        setCommandPaletteLevel(commandPaletteVisible ? 0 : 1)
      }

      // Escape to close
      if (e.key === 'Escape' && commandPaletteVisible) {
        setCommandPaletteVisible(false)
        setCommandPaletteLevel(0)
      }

      // Tab to expand when palette is open
      if (e.key === 'Tab' && commandPaletteVisible) {
        e.preventDefault()
        setCommandPaletteLevel(commandPaletteLevel === 1 ? 2 : 1)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [commandPaletteVisible, commandPaletteLevel])

  // Custom background image handler
  const handleCustomBgUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setCustomBgImage(reader.result)
        setAnimatedBg('custom')
      }
      reader.readAsDataURL(file)
    }
  }

  // Desktop drag and drop handlers
  const handleDesktopDrop = (e) => {
    e.preventDefault()
    setDragOverDesktop(false)

    const data = e.dataTransfer.getData('text/plain')
    if (data) {
      const newItem = {
        id: Date.now(),
        data: data,
        x: e.nativeEvent.offsetX,
        y: e.nativeEvent.offsetY,
        type: data.includes('openai') ? 'openai' : data.includes('claude') ? 'claude' : data.includes('gemini') ? 'gemini' : 'unknown'
      }
      setDesktopItems(prev => [...prev, newItem])
    }
  }

  const handleDesktopDragOver = (e) => {
    e.preventDefault()
    setDragOverDesktop(true)
  }

  const handleDesktopDragLeave = (e) => {
    e.preventDefault()
    setDragOverDesktop(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black relative overflow-hidden text-gray-200" style={{ fontFamily: "'Helvetica Neue', -apple-system, system-ui, sans-serif" }}>
      {/* Optimized Animated Background */}
      {animatedBg !== 'custom' && animatedBg !== 'color' && (
        <AnimatedBackground
          type={animatedBg}
          isActive={true}
        />
      )}

      {/* Solid Color Background */}
      {animatedBg === 'color' && (
        <div
          className="fixed inset-0 z-0"
          style={{ backgroundColor: bgColor }}
        />
      )}

      {/* Custom Background Image */}
      {animatedBg === 'custom' && customBgImage && (
        <div
          className="fixed inset-0 z-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url(${customBgImage})` }}
        />
      )}

      {/* Dynamic Top Bar */}
      <header
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ease-in-out ${showHeader ? 'h-16 opacity-100' : 'h-0 opacity-0'}`}
        onMouseEnter={() => setShowHeader(true)}
        onMouseLeave={() => setShowHeader(false)}
      >
        <div className="flex items-center justify-between p-4 bg-gray-800/80 backdrop-blur-lg border-b border-gray-700">
          <div className="flex items-center gap-4">
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              LUKHΛS
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Input
              placeholder="Search..."
              className="w-64 bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-400 focus:border-blue-400"
            />
            <Button variant="ghost" size="icon" onClick={() => setShowSettings(!showSettings)}>
              <Settings className="w-5 h-5 text-gray-400 hover:text-blue-400" />
            </Button>
            <Button variant="ghost" size="icon">
              <ArrowRight className="w-5 h-5 text-gray-400 hover:text-blue-400" />
            </Button>
            <Button variant="ghost" size="icon">
              <Save className="w-5 h-5 text-gray-400 hover:text-blue-400" />
            </Button>
            <Button
              variant={isLoggedIn ? "ghost" : "default"}
              onClick={() => setIsLoggedIn(!isLoggedIn)}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isLoggedIn ? <User className="w-5 h-5" /> : 'Sign In'}
            </Button>
          </div>
        </div>
      </header>

      {/* Modern Command Palette */}
      <AnimatePresence>
        {commandPaletteVisible && (
          <div
            className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-[20vh]"
            onClick={() => {
              setCommandPaletteVisible(false)
              setCommandPaletteLevel(0)
            }}
          >
            <div
              className={`bg-gray-800/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-gray-700 transition-all duration-300 ease-out overflow-hidden ${
                commandPaletteLevel === 1
                  ? 'w-[90%] max-w-2xl h-[200px]'
                  : 'w-[90%] max-w-4xl h-[400px]'
              }`}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Search Header */}
              <div className="p-4 border-b border-gray-700">
                <div className="flex items-center gap-3">
                  <Search className="w-5 h-5 text-gray-400" />
                  <Input
                    placeholder="Search commands... (Tab to expand, Esc to close)"
                    className="border-0 bg-transparent text-lg focus:ring-0 text-gray-200 placeholder-gray-500"
                    autoFocus
                  />
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <kbd className="px-2 py-1 bg-gray-700 rounded text-gray-300">⌘K</kbd>
                    <span>toggle</span>
                  </div>
                </div>
              </div>

              {/* Command Grid - Only show when expanded */}
              {commandPaletteLevel === 2 && (
                <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-3 overflow-y-auto">
                  {[
                    { icon: Home, label: 'Home', desc: 'Go to homepage' },
                    { icon: FileText, label: 'Documents', desc: 'View documents' },
                    { icon: Image, label: 'Images', desc: 'Browse images' },
                    { icon: Video, label: 'Videos', desc: 'Watch videos' },
                    { icon: Code, label: 'Code', desc: 'Code editor' },
                    { icon: Database, label: 'Data', desc: 'Manage data' },
                    { icon: Cloud, label: 'Cloud', desc: 'Cloud storage' },
                    { icon: Zap, label: 'Quick Actions', desc: 'Fast commands' }
                  ].map((item, index) => (
                    <Button
                      key={index}
                      variant="ghost"
                      className="h-20 flex flex-col items-center gap-2 hover:bg-gray-700 text-gray-200 transition-colors"
                    >
                      <item.icon className="w-6 h-6" />
                      <div className="text-center">
                        <div className="text-sm font-medium">{item.label}</div>
                        <div className="text-xs text-gray-500">{item.desc}</div>
                      </div>
                    </Button>
                  ))}
                </div>
              )}

              {/* Quick Actions - Always visible */}
              {commandPaletteLevel === 1 && (
                <div className="p-4">
                  <div className="text-sm text-gray-400 mb-3">Quick Actions</div>
                  <div className="space-y-2">
                    {[
                      { icon: MessageSquare, label: 'New Chat', shortcut: '⌘N' },
                      { icon: Settings, label: 'Settings', shortcut: '⌘,' },
                      { icon: Search, label: 'Search Files', shortcut: '⌘F' }
                    ].map((item, index) => (
                      <Button
                        key={index}
                        variant="ghost"
                        className="w-full justify-between h-10 hover:bg-gray-700 text-gray-200"
                      >
                        <div className="flex items-center gap-3">
                          <item.icon className="w-4 h-4" />
                          <span>{item.label}</span>
                        </div>
                        <kbd className="px-2 py-1 bg-gray-700 rounded text-xs text-gray-300">
                          {item.shortcut}
                        </kbd>
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </AnimatePresence>

      {/* Studio Layout - Desktop Collaboration */}
      <div className="flex h-[calc(100vh-140px)] relative z-10">
        {/* Left Dock - Conversations & Files */}
        <div
          className={`bg-gray-800/30 backdrop-blur-xl border-r border-gray-700/30 p-4 flex flex-col transition-all duration-300 ${
            showLeftDock ? 'w-80 opacity-100' : 'w-0 opacity-0 overflow-hidden'
          }`}
        >
          {/* LUKHΛS Brand - Top Left */}
          <div className="mb-8">
            <h1 className="text-2xl font-thin text-white tracking-wide" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 100 }}>
              LUKHΛS
            </h1>
          </div>

          {/* Text Tools - Show when in editor mode */}
          {showTextTools && (
            <div className="mb-6 p-3 bg-gray-700/20 rounded-xl border border-gray-600/20">
              <div className="grid grid-cols-4 gap-2">
                {[Bold, Italic, Underline, Link, List, AlignLeft, AlignCenter, AlignRight].map((Icon, i) => (
                  <Button key={i} variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-gray-200 transition-colors">
                    <Icon className="w-4 h-4" />
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Core Applications */}
          <div className="mb-6">
            <div className="grid grid-cols-4 gap-3">
              {[
                { icon: Code, label: 'VSCode', color: 'blue' },
                { icon: Database, label: 'Terminal', color: 'green' },
                { icon: Cloud, label: 'Cloud', color: 'purple' },
                { icon: Settings, label: 'System', color: 'orange' }
              ].map((app, i) => (
                <div key={i} className="group cursor-pointer" title={app.label}>
                  <div className={`w-12 h-12 bg-${app.color}-600/20 rounded-xl border border-${app.color}-500/20 flex items-center justify-center hover:scale-105 transition-all group-hover:bg-${app.color}-600/30`}>
                    <app.icon className={`w-5 h-5 text-${app.color}-400`} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* LUKHΛS Modules */}
          <div className="mb-6">
            <div className="space-y-3">
              {[
                { name: 'ΛLens', desc: 'File Explorer', icon: Search, color: 'blue' },
                { name: 'WΛLLET', desc: 'Identity Vault', icon: User, color: 'green' },
                { name: 'ΛTrace', desc: 'Quantum Trace', icon: Zap, color: 'purple' },
                { name: 'NUBLΛR', desc: 'Cloud Orchestration', icon: Cloud, color: 'orange' },
                { name: 'ΛEon', desc: 'Digital Heirloom', icon: Star, color: 'yellow' },
                { name: 'POETICΛ', desc: 'AI Personality', icon: Heart, color: 'pink' },
                { name: 'Λrgus', desc: 'AR Dashboards', icon: Video, color: 'red' }
              ].map((module, i) => (
                <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-700/20 cursor-pointer transition-colors">
                  <div className={`w-8 h-8 bg-${module.color}-600/20 rounded-lg flex items-center justify-center`}>
                    <module.icon className={`w-4 h-4 text-${module.color}-400`} />
                  </div>
                  <div>
                    <p className="text-sm font-light text-gray-200" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                      {module.name}
                    </p>
                    <p className="text-xs text-gray-500 font-thin">{module.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Conversations */}
          <div className="mb-6">
            <div className="space-y-2">
              {[
                { title: 'Project Planning', time: '2m', active: true },
                { title: 'Code Review', time: '1h', active: false },
                { title: 'Design Discussion', time: '3h', active: false }
              ].map((chat, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    chat.active
                      ? 'bg-blue-600/20 border-blue-500/30 text-blue-200'
                      : 'bg-gray-700/20 border-gray-600/20 text-gray-300 hover:bg-gray-700/30'
                  }`}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `chat-${chat.title.toLowerCase().replace(/\s+/g, '-')}`)
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-light truncate" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                        {chat.title}
                      </p>
                      <p className="text-xs opacity-70 font-thin">{chat.time} ago</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* File Stacks - Simplified */}
          <div className="flex-1">
            <div className="space-y-3">
              {[
                { type: 'docs', icon: FileText, count: 3, color: 'blue' },
                { type: 'images', icon: Image, count: 8, color: 'purple' },
                { type: 'code', icon: Code, count: 12, color: 'green' }
              ].map((stack, i) => (
                <div
                  key={i}
                  className="relative group cursor-pointer"
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `file-stack-${stack.type}`)
                  }}
                >
                  <div className="relative">
                    <div className="absolute inset-0 bg-gray-600/10 rounded-lg transform rotate-1 translate-x-0.5 translate-y-0.5"></div>
                    <div className="absolute inset-0 bg-gray-600/20 rounded-lg transform -rotate-1 translate-x-1 translate-y-1"></div>

                    <div className={`relative p-3 bg-gray-700/20 rounded-lg border border-gray-600/20 hover:border-${stack.color}-500/30 transition-all`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 bg-${stack.color}-600/20 rounded-lg flex items-center justify-center`}>
                          <stack.icon className={`w-4 h-4 text-${stack.color}-400`} />
                        </div>
                        <div>
                          <p className="text-sm font-light text-gray-200 capitalize" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                            {stack.type}
                          </p>
                          <p className="text-xs text-gray-500 font-thin">{stack.count}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
          {/* Text Tools - Show when in editor mode */}
          {showTextTools && (
            <div className="mb-4 p-3 bg-gray-700/30 rounded-lg border border-gray-600/30">
              <h4 className="text-sm font-medium text-gray-300 mb-3">Text Tools</h4>
              <div className="grid grid-cols-4 gap-2">
                {[Bold, Italic, Underline, Link, List, AlignLeft, AlignCenter, AlignRight].map((Icon, i) => (
                  <Button key={i} variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-gray-200">
                    <Icon className="w-4 h-4" />
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Conversations */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Conversations</h3>
            <div className="space-y-2">
              {[
                { title: 'Project Planning', time: '2m', active: true },
                { title: 'Code Review', time: '1h', active: false },
                { title: 'Design Discussion', time: '3h', active: false },
                { title: 'API Integration', time: '1d', active: false }
              ].map((chat, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    chat.active
                      ? 'bg-blue-600/20 border-blue-500/50 text-blue-200'
                      : 'bg-gray-700/20 border-gray-600/30 text-gray-300 hover:bg-gray-700/30'
                  }`}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `chat-${chat.title.toLowerCase().replace(/\s+/g, '-')}`)
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{chat.title}</p>
                      <p className="text-xs opacity-70">{chat.time} ago</p>
                    </div>
                    <div className="text-xs text-gray-500">
                      ⋮⋮
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>              {/* File Stacks - Apple Style */}
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-300 mb-3">Files</h3>
                <div className="space-y-4">
                  {[
                    { type: 'docs', icon: FileText, items: ['project.md', 'notes.txt', 'readme.md'], color: 'blue' },
                    { type: 'images', icon: Image, items: ['logo.png', 'mockup.jpg', 'icons.svg'], color: 'purple' },
                    { type: 'code', icon: Code, items: ['main.py', 'utils.js', 'styles.css'], color: 'green' }
                  ].map((stack, i) => (
                    <div
                      key={i}
                      className="relative group cursor-pointer"
                      onMouseEnter={() => setExpandedStack(i)}
                      onMouseLeave={() => setExpandedStack(null)}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData('text/plain', `file-stack-${stack.type}`)
                      }}
                    >
                      {/* Stack Base */}
                      <div className="relative">
                        {/* Background stack layers */}
                        <div className="absolute inset-0 bg-gray-600/20 rounded-lg transform rotate-1 translate-x-0.5 translate-y-0.5"></div>
                        <div className="absolute inset-0 bg-gray-600/30 rounded-lg transform -rotate-1 translate-x-1 translate-y-1"></div>

                        {/* Main stack */}
                        <div className={`relative p-3 bg-gray-700/30 rounded-lg border border-gray-600/30 hover:border-${stack.color}-500/50 transition-all`}>
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 bg-${stack.color}-600/20 rounded-lg flex items-center justify-center`}>
                              <stack.icon className={`w-4 h-4 text-${stack.color}-400`} />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-200 capitalize">{stack.type}</p>
                              <p className="text-xs text-gray-500">{stack.items.length} items</p>
                            </div>
                          </div>
                        </div>

                        {/* Hover expansion */}
                        <div className={`absolute top-0 left-full ml-2 transition-all duration-200 z-50 ${
                          expandedStack === i ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
                        }`}>
                          <div className="bg-gray-800/95 backdrop-blur rounded-lg border border-gray-700 p-2 min-w-[200px]">
                            {stack.items.map((file, fi) => (
                              <div
                                key={fi}
                                className="flex items-center gap-2 p-2 hover:bg-gray-700/50 rounded text-sm text-gray-300 cursor-pointer"
                                draggable
                                onDragStart={(e) => {
                                  e.dataTransfer.setData('text/plain', `file-${file}`)
                                  e.stopPropagation()
                                }}
                              >
                                <stack.icon className="w-3 h-3" />
                                <span>{file}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
        </div>

        {/* Main Studio Canvas */}
        <div className="flex-1 flex flex-col">
          {/* Clean Desktop Workspace */}
          <div className="flex-1 p-8 overflow-auto">
            <div className="max-w-6xl mx-auto h-full">
              {/* Drag & Drop Desktop */}
              <div
                className={`flex-1 min-h-[500px] rounded-2xl relative transition-all duration-300 ${
                  dragOverDesktop
                    ? 'border-2 border-dashed border-blue-500/70 bg-blue-900/10 backdrop-blur'
                    : 'border-0'
                }`}
                onDragOver={handleDesktopDragOver}
                onDragLeave={handleDesktopDragLeave}
                onDrop={handleDesktopDrop}
              >
                {/* Drop Zone Hint - Only visible when dragging */}
                {dragOverDesktop && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-600/30 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Plus className="w-8 h-8 text-blue-400" />
                      </div>
                      <p className="text-blue-300 text-lg mb-2">Drop here to collaborate</p>
                    </div>
                  </div>
                )}

                {/* Desktop Items */}
                {desktopItems.map((item) => (
                  <div
                    key={item.id}
                    className="absolute p-3 bg-gray-800/80 backdrop-blur-xl rounded-xl border border-gray-600/30 cursor-move hover:scale-105 transition-all"
                    style={{ left: item.x, top: item.y }}
                    draggable
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        item.type === 'openai' ? 'bg-green-600/20' :
                        item.type === 'claude' ? 'bg-orange-600/20' :
                        item.type === 'gemini' ? 'bg-purple-600/20' : 'bg-gray-600/20'
                      }`}>
                        {item.type === 'openai' && <Zap className="w-4 h-4 text-green-400" />}
                        {item.type === 'claude' && <User className="w-4 h-4 text-orange-400" />}
                        {item.type === 'gemini' && <Star className="w-4 h-4 text-purple-400" />}
                        {item.type === 'unknown' && <FileText className="w-4 h-4 text-gray-400" />}
                      </div>
                      <span className="text-sm text-gray-200 font-light" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                        {item.data.replace(/^[a-z]+-/, '')}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-gray-500 hover:text-red-400"
                        onClick={() => setDesktopItems(prev => prev.filter(i => i.id !== item.id))}
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Dock - AI Agents */}
        <div
          className={`bg-gray-800/30 backdrop-blur-xl border-l border-gray-700/30 p-4 flex flex-col transition-all duration-300 ${
            showRightDock ? 'w-64 opacity-100' : 'w-0 opacity-0 overflow-hidden'
          }`}
        >
          {/* OpenAI */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-5 h-5 bg-gradient-to-br from-green-500 to-blue-500 rounded-md"></div>
              <span className="text-sm font-light text-gray-200" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>OpenAI</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {[
                { name: 'GPT-4', icon: MessageSquare },
                { name: 'O1', icon: Star },
                { name: 'DALL-E', icon: Image },
                { name: 'Whisper', icon: Video }
              ].map((model, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-700/20 rounded-lg border border-gray-600/20 hover:border-green-500/30 cursor-pointer transition-all group"
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `openai-${model.name.toLowerCase()}`)
                  }}
                >
                  <div className="flex flex-col items-center gap-1">
                    <model.icon className="w-4 h-4 text-gray-400 group-hover:text-green-400" />
                    <span className="text-xs text-gray-400 group-hover:text-gray-200 font-thin">{model.name}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Claude */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-5 h-5 bg-gradient-to-br from-orange-500 to-red-500 rounded-md"></div>
              <span className="text-sm font-light text-gray-200" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>Claude</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {[
                { name: 'Sonnet', icon: Edit },
                { name: 'Haiku', icon: FileText }
              ].map((model, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-700/20 rounded-lg border border-gray-600/20 hover:border-orange-500/30 cursor-pointer transition-all group"
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `claude-${model.name.toLowerCase()}`)
                  }}
                >
                  <div className="flex flex-col items-center gap-1">
                    <model.icon className="w-4 h-4 text-gray-400 group-hover:text-orange-400" />
                    <span className="text-xs text-gray-400 group-hover:text-gray-200 font-thin">{model.name}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Gemini */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-purple-500 rounded-md"></div>
              <span className="text-sm font-light text-gray-200" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>Gemini</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {[
                { name: 'Pro', icon: MessageSquare },
                { name: 'Flash', icon: Zap }
              ].map((model, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-700/20 rounded-lg border border-gray-600/20 hover:border-purple-500/30 cursor-pointer transition-all group"
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `gemini-${model.name.toLowerCase()}`)
                  }}
                >
                  <div className="flex flex-col items-center gap-1">
                    <model.icon className="w-4 h-4 text-gray-400 group-hover:text-purple-400" />
                    <span className="text-xs text-gray-400 group-hover:text-gray-200 font-thin">{model.name}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Sessions */}
          <div className="flex-1 mt-auto">
            <div className="space-y-1">
              <div className="p-2 bg-blue-900/20 rounded border border-blue-500/20 text-xs">
                <div className="flex items-center gap-2 text-blue-300">
                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full"></div>
                  <span className="font-thin">O1 Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Minimal Chat Bar - Bottom */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800/60 backdrop-blur border-t border-gray-700/50 p-4 z-20">
        <div className="max-w-6xl mx-auto">
          {/* Text Tools */}
          {showTextTools && (
            <div className="mb-3 p-2 bg-gray-700/30 rounded-lg flex gap-1">
              {[Bold, Italic, Underline, Link].map((Icon, i) => (
                <Button key={i} variant="ghost" size="sm" className="h-7 w-7 p-0 text-gray-400 hover:text-gray-200">
                  <Icon className="w-3.5 h-3.5" />
                </Button>
              ))}
            </div>
          )}

          {/* Chat Input Row */}
          <div className="flex items-center gap-3 mb-3">
            {/* Main Input */}
            <div className="flex-1 relative">
              <Input
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Chat with AI agents to collaborate..."
                className="pr-20 bg-gray-700/50 border-gray-600/50 focus:border-blue-500 text-gray-200 h-12 text-lg"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    // Handle send message
                  }
                }}
              />

              <Button variant="ghost" size="sm" className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0 text-gray-400">
                <Smile className="w-4 h-4" />
              </Button>
            </div>

            {/* Send Button */}
            <Button className="bg-blue-600 hover:bg-blue-700 h-12 w-12 p-0" title="Send">
              <Send className="w-5 h-5" />
            </Button>
          </div>

          {/* Icons Row - Below Input */}
          <div className="flex items-center justify-between">
            {/* Left: Mode Icons */}
            <div className="flex items-center gap-2">
              {[
                { id: 'chat', icon: MessageSquare, tooltip: 'Chat' },
                { id: 'code', icon: Code, tooltip: 'Code' },
                { id: 'creative', icon: Star, tooltip: 'Creative' }
              ].map((mode) => (
                <Button key={mode.id} variant="ghost" size="sm" onClick={() => setChatMode(mode.id)}
                  className={`h-8 w-8 p-0 ${chatMode === mode.id ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-300'}`}
                  title={mode.tooltip}>
                  <mode.icon className="w-4 h-4" />
                </Button>
              ))}
            </div>

            {/* Center: Tool Icons */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowTextTools(!showTextTools)}
                className="h-8 w-8 p-0 text-gray-400 hover:text-blue-400" title="Text tools">
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-blue-400" title="Attach">
                <Paperclip className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-green-400" title="Share to agents">
                <Share className="w-4 h-4" />
              </Button>
            </div>

            {/* Right: Dock Controls */}
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowLeftDock(!showLeftDock)}
                className="h-8 w-8 p-0 text-gray-400 hover:text-blue-400" title="Toggle tools">
                <Menu className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setShowRightDock(!showRightDock)}
                className="h-8 w-8 p-0 text-gray-400 hover:text-blue-400" title="Toggle agents">
                <User className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-gray-900 rounded-2xl p-6 w-96 max-h-[80vh] overflow-y-auto border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-100">Settings</h2>
              <Button variant="ghost" size="icon" onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-blue-400">
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-100">Background</h3>
                <div className="grid grid-cols-2 gap-2 mb-4">
                  {[
                    { label: 'Stars', value: 'stars' },
                    { label: 'Constellation', value: 'constellation' },
                    { label: 'Geometric', value: 'geometric' },
                    { label: 'Clouds', value: 'clouds' },
                    { label: 'Solid Color', value: 'color' },
                    { label: 'Custom Image', value: 'custom' }
                  ].map((bgOption) => (
                    <Button
                      key={bgOption.value}
                      variant={animatedBg === bgOption.value ? "default" : "outline"}
                      onClick={() => setAnimatedBg(bgOption.value)}
                      className="capitalize text-xs"
                    >
                      {bgOption.label}
                    </Button>
                  ))}
                </div>

                {/* Color Picker */}
                {animatedBg === 'color' && (
                  <div className="mt-4">
                    <label htmlFor="bg-color" className="block text-sm font-medium text-gray-300 mb-2">Background Color</label>
                    <input
                      id="bg-color"
                      type="color"
                      value={bgColor}
                      onChange={(e) => setBgColor(e.target.value)}
                      className="w-full h-10 rounded border border-gray-600 bg-gray-800"
                    />
                  </div>
                )}

                {/* Custom Image Upload */}
                {animatedBg === 'custom' && (
                  <div className="mt-4">
                    <label htmlFor="custom-bg-upload" className="block text-sm font-medium text-gray-300 mb-2">Upload Custom Image</label>
                    <input
                      id="custom-bg-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleCustomBgUpload}
                      className="block w-full text-sm text-gray-400
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                    />
                  </div>
                )}
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-100">Theme</h3>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    Light Mode
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    Dark Mode
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    Auto
                  </Button>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-100">Notifications</h3>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-gray-200">
                    <input type="checkbox" defaultChecked className="form-checkbox text-blue-600 bg-gray-700 border-gray-600" />
                    <span>Email notifications</span>
                  </label>
                  <label className="flex items-center gap-2 text-gray-200">
                    <input type="checkbox" defaultChecked className="form-checkbox text-blue-600 bg-gray-700 border-gray-600" />
                    <span>Push notifications</span>
                  </label>
                  <label className="flex items-center gap-2 text-gray-200">
                    <input type="checkbox" className="form-checkbox text-blue-600 bg-gray-700 border-gray-600" />
                    <span>SMS notifications</span>
                  </label>
                </div>
              </div>

              {/* New Connectors Section */}
              <div>
                <h3 className="text-lg font-semibold mb-3 text-gray-100">Connectors</h3>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    <Twitter className="w-4 h-4 mr-2" />
                    Connect Twitter
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    <BarChart2 className="w-4 h-4 mr-2" />
                    Connect TradingView
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    <Mail className="w-4 h-4 mr-2" />
                    Connect Email
                  </Button>
                  <Button variant="outline" className="w-full justify-start border-gray-600 text-gray-200 hover:bg-gray-700">
                    <CloudIcon className="w-4 h-4 mr-2" />
                    Connect Cloud Storage
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
