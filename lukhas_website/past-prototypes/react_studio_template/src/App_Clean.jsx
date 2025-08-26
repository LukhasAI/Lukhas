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
  Terminal,
  Twitter,
  Mail,
  Cloud as CloudIcon,
  BarChart2
} from 'lucide-react'
import './App.css'

function App() {
  const [commandPaletteVisible, setCommandPaletteVisible] = useState(false)
  const [commandPaletteLevel, setCommandPaletteLevel] = useState(0)
  const [chatMessage, setChatMessage] = useState('')
  const [showTextTools, setShowTextTools] = useState(false)
  const [showSendOptions, setShowSendOptions] = useState(false)
  const [keySequence, setKeySequence] = useState([])
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [animatedBg, setAnimatedBg] = useState('constellation')
  const [bgColor, setBgColor] = useState('#1a1a2e')
  const [customBgImage, setCustomBgImage] = useState(null)
  const [showLeftDock, setShowLeftDock] = useState(true)
  const [showRightDock, setShowRightDock] = useState(true)
  const [showHeader, setShowHeader] = useState(false)
  const [chatMode, setChatMode] = useState('chat')
  const [desktopItems, setDesktopItems] = useState([])
  const [dragOverDesktop, setDragOverDesktop] = useState(false)
  const [expandedStack, setExpandedStack] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState('OpenAI O1')

  const sendButtonRef = useRef(null)

  // Show text tools only in dedicated text editing mode (not code mode)
  useEffect(() => {
    // Text tools only appear in text editing mode (not code mode)
    setShowTextTools(chatMode === 'text')
  }, [chatMode])

  // Simplified keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteVisible(!commandPaletteVisible)
        setCommandPaletteLevel(commandPaletteVisible ? 0 : 1)
      }

      if (e.key === 'Escape' && commandPaletteVisible) {
        setCommandPaletteVisible(false)
        setCommandPaletteLevel(0)
      }

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

      {/* Command Palette */}
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
                  ? 'w-[90%] max-w-2xl h-[300px]'
                  : 'w-[90%] max-w-4xl h-[500px]'
              }`}
              onClick={(e) => e.stopPropagation()}
            >
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

              {/* Command palette content */}
              <div className="p-4 space-y-4 overflow-y-auto">
                {commandPaletteLevel === 2 && (
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-gray-100">Background Settings</h3>
                      <div className="grid grid-cols-2 gap-3">
                        {[
                          { type: 'constellation', name: 'Constellation', active: animatedBg === 'constellation' },
                          { type: 'clouds', name: 'Clouds', active: animatedBg === 'clouds' },
                          { type: 'color', name: 'Solid Color', active: animatedBg === 'color' },
                          { type: 'custom', name: 'Custom Image', active: animatedBg === 'custom' }
                        ].map((bg) => (
                          <Button
                            key={bg.type}
                            variant={bg.active ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setAnimatedBg(bg.type)}
                            className="justify-start"
                          >
                            {bg.name}
                          </Button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-gray-100">Interface</h3>
                      <div className="space-y-2">
                        <Button variant="ghost" size="sm" onClick={() => setShowLeftDock(!showLeftDock)} className="w-full justify-start">
                          {showLeftDock ? 'Hide' : 'Show'} Left Dock
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setShowRightDock(!showRightDock)} className="w-full justify-start">
                          {showRightDock ? 'Hide' : 'Show'} Right Dock
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Fullscreen Mode
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Zen Mode
                        </Button>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-gray-100">Accessibility</h3>
                      <div className="space-y-2">
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          High Contrast
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Reduce Motion
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Large Text
                        </Button>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold mb-3 text-gray-100">AI Settings</h3>
                      <div className="space-y-2">
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Model Preferences
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          API Configuration
                        </Button>
                        <Button variant="ghost" size="sm" className="w-full justify-start">
                          Response Length
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {commandPaletteLevel === 1 && (
                  <div className="space-y-2">
                    <div className="text-sm text-gray-400 mb-2">Quick Commands</div>
                    <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => setCommandPaletteLevel(2)}>
                      <Settings className="w-4 h-4 mr-2" />
                      Settings & Preferences
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <Code className="w-4 h-4 mr-2" />
                      Open Code Editor
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <Terminal className="w-4 h-4 mr-2" />
                      Open Terminal
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <FileText className="w-4 h-4 mr-2" />
                      New Document
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <Search className="w-4 h-4 mr-2" />
                      Find in Files
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <User className="w-4 h-4 mr-2" />
                      Switch AI Model
                    </Button>
                    <Button variant="ghost" size="sm" className="w-full justify-start">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      New Chat Session
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </AnimatePresence>

      {/* Studio Layout */}
      <div className="flex h-screen relative z-10">
        {/* Left Dock */}
        <div
          className={`bg-gray-800/30 backdrop-blur-xl border-r border-gray-700/30 p-4 flex flex-col transition-all duration-300 ${
            showLeftDock ? 'w-56 opacity-100' : 'w-0 opacity-0 overflow-hidden'
          }`}
        >
          {/* Settings Button and LUKHΛS Brand */}
          <div className="mb-8 flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-slate-400 hover:text-slate-300 rounded-lg"
              onClick={() => setShowSettings(!showSettings)}
              title="Settings"
            >
              <div className="flex flex-col items-center justify-center gap-0.5">
                <div className="w-3 h-0.5 bg-current rounded-full"></div>
                <div className="w-3 h-0.5 bg-current rounded-full"></div>
                <div className="w-3 h-0.5 bg-current rounded-full"></div>
              </div>
            </Button>
            <h1 className="text-2xl text-white tracking-wide flex-1 text-center" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 100 }}>
              LUKHΛS
            </h1>
            <div className="w-8"></div> {/* Spacer for alignment */}
          </div>

          {/* Text Tools - Show when in editor mode */}
          {showTextTools && (
            <div className="mb-6 p-3 bg-gray-700/20 rounded-xl border border-gray-600/20">
              <div className="grid grid-cols-4 gap-2">
                {[Bold, Italic, Underline, Link, List, AlignLeft, AlignCenter, AlignRight].map((Icon, i) => (
                  <Button key={i} variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-slate-300 transition-colors">
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
                { icon: Code, tooltip: 'VSCode', color: 'slate' },
                { icon: Database, tooltip: 'Terminal', color: 'slate' },
                { icon: Cloud, tooltip: 'Cloud Storage', color: 'slate' }
              ].map((app, i) => (
                <div key={i} className="group cursor-pointer" title={app.tooltip}>
                  <div className="w-12 h-12 bg-slate-700/20 rounded-xl border border-slate-600/20 flex items-center justify-center hover:scale-105 transition-all group-hover:bg-slate-700/30">
                    <app.icon className="w-5 h-5 text-slate-500" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* LUKHΛS Modules */}
          <div className="mb-6">
            <div className="grid grid-cols-3 gap-1">
              {[
                { name: 'ΛLens', icon: Search, color: 'slate' },
                { name: 'WΛLLET', icon: User, color: 'slate' },
                { name: 'ΛTrace', icon: Zap, color: 'slate' },
                { name: 'NUBLΛR', icon: Cloud, color: 'slate' },
                { name: 'ΛEon', icon: Star, color: 'slate' },
                { name: 'POETICΛ', icon: Heart, color: 'slate' },
                { name: 'Λrgus', icon: Video, color: 'slate' }
              ].map((module, i) => (
                <div key={i} className="flex flex-col items-center gap-1 p-1 rounded-lg hover:bg-slate-700/20 cursor-pointer transition-colors group">
                  <div className="w-5 h-5 bg-slate-700/20 rounded flex items-center justify-center">
                    <module.icon className="w-3 h-3 text-slate-500" />
                  </div>
                  <p className="text-[10px] text-slate-400 text-center" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                    {module.name}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Conversations */}
          <div className="flex-1">
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
                      ? 'bg-slate-600/20 border-slate-500/30 text-slate-200'
                      : 'bg-slate-700/20 border-slate-600/20 text-slate-300 hover:bg-slate-700/30'
                  }`}
                  draggable
                  onDragStart={(e) => {
                    e.dataTransfer.setData('text/plain', `chat-${chat.title.toLowerCase().replace(/\s+/g, '-')}`)
                  }}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-slate-500 to-slate-600 rounded-lg flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm truncate" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>
                        {chat.title}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Desktop Area */}
        <div className="flex-1 relative p-6">
          <div
            className={`h-full relative rounded-3xl transition-all duration-300 ${
              dragOverDesktop ? 'border-2 border-dashed border-blue-400 bg-blue-400/5' : ''
            }`}
            onDragOver={handleDesktopDragOver}
            onDragLeave={handleDesktopDragLeave}
            onDrop={handleDesktopDrop}
          >
            {dragOverDesktop && (
              <div className="absolute inset-0 flex items-center justify-center bg-blue-400/10 rounded-3xl">
                <div className="text-blue-400 text-lg font-medium">Drop items here</div>
              </div>
            )}

            {/* Desktop Items */}
            {desktopItems.map((item) => (
              <div
                key={item.id}
                className="absolute bg-gray-700/80 backdrop-blur-sm border border-gray-600/50 rounded-xl p-4 shadow-lg"
                style={{ left: item.x, top: item.y }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                    {item.type === 'chat' && <MessageSquare className="w-5 h-5 text-white" />}
                    {item.type === 'openai' && <Star className="w-5 h-5 text-white" />}
                    {item.type === 'claude' && <Edit className="w-5 h-5 text-white" />}
                    {item.type === 'gemini' && <Zap className="w-5 h-5 text-white" />}
                  </div>
                  <div>
                    <p className="text-sm text-gray-200 font-medium">{item.data}</p>
                    <p className="text-xs text-gray-400">{item.type}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Dock - Compact AI Agents */}
        <div
          className={`bg-gray-800/30 backdrop-blur-xl border-l border-gray-700/30 p-4 flex flex-col transition-all duration-300 ${
            showRightDock ? 'w-48 opacity-100' : 'w-0 opacity-0 overflow-hidden'
          }`}
        >
          {/* Agent Selector - Compact */}
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-4 h-4 bg-gradient-to-br from-slate-500 to-slate-600 rounded-sm"></div>
              <span className="text-sm text-gray-200 font-medium" style={{ fontFamily: "'Helvetica Neue', sans-serif", fontWeight: 300 }}>AI Agents</span>
            </div>

            {/* Active Agent Display */}
            <div className="p-3 bg-blue-900/20 rounded-xl border border-blue-500/20 mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <Star className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-blue-200 font-medium">{selectedAgent}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                    <span className="text-xs text-blue-300">Active</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Agent Switcher */}
            <div className="space-y-1">
              {[
                { name: 'GPT-4', provider: 'OpenAI', icon: MessageSquare, color: 'slate' },
                { name: 'Claude Sonnet', provider: 'Anthropic', icon: Edit, color: 'orange' },
                { name: 'Gemini Pro', provider: 'Google', icon: Zap, color: 'purple' }
              ].map((agent, i) => (
                <div
                  key={i}
                  className={`p-2 bg-gray-700/20 rounded-lg border cursor-pointer transition-all group ${
                    selectedAgent === agent.name
                      ? `border-${agent.color}-500/30 bg-${agent.color}-900/20`
                      : 'border-gray-600/20 hover:border-slate-500/30'
                  }`}
                  onClick={() => setSelectedAgent(agent.name)}
                >
                  <div className="flex items-center gap-2">
                    <agent.icon className={`w-3 h-3 ${
                      selectedAgent === agent.name
                        ? `text-${agent.color}-400`
                        : `text-gray-400 group-hover:text-${agent.color}-400`
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-xs truncate ${
                        selectedAgent === agent.name
                          ? 'text-gray-200'
                          : 'text-gray-300 group-hover:text-gray-200'
                      }`}>{agent.name}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Additional Tools - Compact */}
          <div className="mb-4">
            <div className="text-xs text-gray-400 mb-2">Tools</div>
            <div className="space-y-1">
              {[
                { name: 'Voice Morph', icon: Video, desc: 'Research Preview' },
                { name: 'Data Engine', icon: Database, desc: 'Analytics' },
                { name: 'Widgets', icon: BarChart2, desc: 'Dashboard' }
              ].map((tool, i) => (
                <div
                  key={i}
                  className="p-2 bg-gray-700/20 rounded-lg border border-gray-600/20 hover:border-slate-500/30 cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-2">
                    <tool.icon className="w-3 h-3 text-gray-400 group-hover:text-slate-300" />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-gray-300 group-hover:text-gray-200 truncate">{tool.name}</p>
                      <p className="text-xs text-gray-500 truncate">{tool.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Status */}
          <div className="mt-auto">
            <div className="p-2 bg-gray-700/20 rounded-lg border border-gray-600/20">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-xs text-gray-300">System Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Chat Interface - 3D Effect - Contained within Desktop */}
      <div className="fixed bottom-6 z-40" style={{
        left: showLeftDock ? '15rem' : '1.5rem',
        right: showRightDock ? '13rem' : '1.5rem',
        transition: 'left 300ms, right 300ms'
      }}>
        <div
          className="bg-gray-800/90 backdrop-blur-xl rounded-3xl shadow-2xl border border-gray-700/50 p-4"
          style={{
            boxShadow: `
              0 25px 50px -12px rgba(0, 0, 0, 0.5),
              0 8px 16px -8px rgba(0, 0, 0, 0.3),
              inset 0 1px 0 rgba(255, 255, 255, 0.1)
            `
          }}
        >
          {/* Chat Input */}
          <div className="flex items-center gap-4 mb-3">
            <div className="flex-1 relative">
              <Input
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Chat with AI agents to collaborate..."
                className="pr-20 bg-gray-700/50 border-gray-600/50 focus:border-slate-500 text-gray-200 h-12 text-base rounded-2xl"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                  }
                }}
              />

              <Button variant="ghost" size="sm" className="absolute right-3 top-1/2 -translate-y-1/2 h-6 w-6 p-0 text-gray-400 hover:text-slate-300">
                <Smile className="w-4 h-4" />
              </Button>
            </div>

            <Button className="bg-slate-600 hover:bg-slate-700 h-12 w-12 p-0 rounded-2xl shadow-lg" title="Send">
              <Send className="w-4 h-4" />
            </Button>
          </div>

          {/* Mode Icons & Controls - Reorganized Logically */}
          <div className="flex items-center justify-between">
            {/* Left: Chat Modes */}
            <div className="flex items-center gap-2">
              {[
                { id: 'chat', icon: MessageSquare, tooltip: 'Chat' },
                { id: 'code', icon: Code, tooltip: 'Code' },
                { id: 'text', icon: Edit, tooltip: 'Text' },
                { id: 'creative', icon: Star, tooltip: 'Creative' }
              ].map((mode) => (
                <Button key={mode.id} variant="ghost" size="sm" onClick={() => setChatMode(mode.id)}
                  className={`h-8 w-8 p-0 rounded-xl ${chatMode === mode.id ? 'bg-slate-600 text-white shadow-md' : 'text-gray-500 hover:text-slate-300 hover:bg-gray-700/50'}`}
                  title={mode.tooltip}>
                  <mode.icon className="w-3 h-3" />
                </Button>
              ))}
            </div>

            {/* Right: Action Controls */}
            <div className="flex items-center gap-2">
              {/* Add Items Dropdown */}
              <div className="relative">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-gray-400 hover:text-slate-300 rounded-xl"
                  title="Add items"
                  onClick={() => setShowSendOptions(!showSendOptions)}
                >
                  <Plus className="w-3 h-3" />
                </Button>

                {showSendOptions && (
                  <div className="absolute bottom-full mb-2 left-0 bg-gray-800/95 backdrop-blur-lg rounded-xl border border-gray-700/50 p-2 shadow-xl z-50">
                    <div className="flex flex-col gap-1 min-w-[120px]">
                      <Button variant="ghost" size="sm" className="justify-start h-8 text-xs text-gray-300 hover:text-white">
                        <FileText className="w-3 h-3 mr-2" />
                        Add Document
                      </Button>
                      <Button variant="ghost" size="sm" className="justify-start h-8 text-xs text-gray-300 hover:text-white">
                        <Image className="w-3 h-3 mr-2" />
                        Add Image
                      </Button>
                      <Button variant="ghost" size="sm" className="justify-start h-8 text-xs text-gray-300 hover:text-white">
                        <Code className="w-3 h-3 mr-2" />
                        Add Code
                      </Button>
                      <Button variant="ghost" size="sm" className="justify-start h-8 text-xs text-gray-300 hover:text-white">
                        <Paperclip className="w-3 h-3 mr-2" />
                        Attach File
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-slate-300 rounded-xl" title="Attach">
                <Paperclip className="w-3 h-3" />
              </Button>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-gray-400 hover:text-slate-300 rounded-xl" title="Share to agents">
                <Share className="w-3 h-3" />
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
                    { label: 'Constellation', value: 'constellation' },
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
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
