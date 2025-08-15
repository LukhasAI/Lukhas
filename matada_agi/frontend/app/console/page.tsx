'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// Icons (using simple SVG implementations)
const TerminalIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
  </svg>
)

const NetworkIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
)

const MemoryIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
  </svg>
)

const ShieldIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
)

const LogsIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
)

const ApiIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
  </svg>
)

const SearchIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
)

interface TabConfig {
  id: string
  label: string
  icon: React.ReactNode
  component: React.ReactNode
}

// Terminal Component
const Terminal = () => {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState<string[]>([
    '$ MATADA Console v1.0.0 initialized',
    '$ Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian',
    '$ Type "help" for available commands',
    ''
  ])
  const terminalRef = useRef<HTMLDivElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const newHistory = [...history, `$ ${input}`]
    
    // Simple command handling
    switch (input.toLowerCase().trim()) {
      case 'help':
        newHistory.push('Available commands:')
        newHistory.push('  status    - Show system status')
        newHistory.push('  nodes     - List active nodes')
        newHistory.push('  memory    - Show memory fold status')
        newHistory.push('  guardian  - Show Guardian metrics')
        newHistory.push('  clear     - Clear terminal')
        newHistory.push('  help      - Show this help')
        break
      case 'status':
        newHistory.push('MATADA System Status: ACTIVE')
        newHistory.push('⚛️ Identity Engine: ONLINE')
        newHistory.push('🧠 Consciousness Engine: ACTIVE')
        newHistory.push('🛡️ Guardian System: PROTECTING')
        newHistory.push('Drift Score: 0.03 (HEALTHY)')
        break
      case 'nodes':
        newHistory.push('Active Nodes:')
        newHistory.push('  fact_node_001    [READY]')
        newHistory.push('  math_node_002    [ACTIVE]')
        newHistory.push('  validator_003    [MONITORING]')
        newHistory.push('  memory_fold_004  [PROCESSING]')
        break
      case 'memory':
        newHistory.push('Memory Fold System:')
        newHistory.push('  Total Folds: 847')
        newHistory.push('  Active Chains: 23')
        newHistory.push('  Cascade Prevention: 99.7%')
        newHistory.push('  Memory Coherence: STABLE')
        break
      case 'guardian':
        newHistory.push('Guardian System Metrics:')
        newHistory.push('  Ethics Score: 0.97 (EXCELLENT)')
        newHistory.push('  Drift Detection: ACTIVE')
        newHistory.push('  Repair Operations: 0')
        newHistory.push('  Trust Level: HIGH')
        break
      case 'clear':
        setHistory(['$ MATADA Console cleared'])
        setInput('')
        return
      default:
        newHistory.push(`Command not found: ${input}`)
        newHistory.push('Type "help" for available commands')
    }

    newHistory.push('')
    setHistory(newHistory)
    setInput('')
  }

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [history])

  return (
    <div className="h-full flex flex-col bg-black/50 rounded-lg border border-white/10">
      <div className="flex items-center justify-between p-3 border-b border-white/10">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
        <span className="text-xs text-white/60 font-mono">MATADA Terminal</span>
      </div>
      <div ref={terminalRef} className="flex-1 p-4 overflow-y-auto font-mono text-sm">
        {history.map((line, i) => (
          <div key={i} className={line.startsWith('$') ? 'text-trinity-consciousness' : 'text-white/80'}>
            {line}
          </div>
        ))}
        <form onSubmit={handleSubmit} className="flex items-center mt-2">
          <span className="text-trinity-consciousness mr-2">$</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-transparent text-white outline-none"
            placeholder="Enter command..."
            autoFocus
          />
        </form>
      </div>
    </div>
  )
}

// Node Graph Component
const NodeGraph = () => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const nodes = [
    { id: 'fact_001', x: 150, y: 100, type: 'fact', status: 'active' },
    { id: 'math_002', x: 300, y: 180, type: 'math', status: 'processing' },
    { id: 'validator_003', x: 450, y: 120, type: 'validator', status: 'monitoring' },
    { id: 'memory_004', x: 250, y: 300, type: 'memory', status: 'stable' },
  ]

  const connections = [
    { from: 'fact_001', to: 'math_002' },
    { from: 'math_002', to: 'validator_003' },
    { from: 'validator_003', to: 'memory_004' },
    { from: 'memory_004', to: 'fact_001' },
  ]

  return (
    <div className="h-full glass-panel rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-regular text-sm tracking-widest uppercase">Node Network</h3>
        <div className="flex items-center space-x-2 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-trinity-consciousness"></div>
            <span>Active</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-accent-gold"></div>
            <span>Processing</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-trinity-guardian"></div>
            <span>Stable</span>
          </div>
        </div>
      </div>
      <div className="relative h-96 bg-black/30 rounded border border-white/10 overflow-hidden">
        <svg className="absolute inset-0 w-full h-full">
          {connections.map((conn, i) => {
            const fromNode = nodes.find(n => n.id === conn.from)
            const toNode = nodes.find(n => n.id === conn.to)
            if (!fromNode || !toNode) return null
            
            return (
              <line
                key={i}
                x1={fromNode.x}
                y1={fromNode.y}
                x2={toNode.x}
                y2={toNode.y}
                stroke="rgba(255,255,255,0.2)"
                strokeWidth="1"
                strokeDasharray="2,2"
              />
            )
          })}
        </svg>
        {nodes.map((node) => (
          <div
            key={node.id}
            className={`absolute w-8 h-8 rounded-full border-2 cursor-pointer transform -translate-x-1/2 -translate-y-1/2 transition-all ${
              node.status === 'active' ? 'bg-trinity-consciousness border-trinity-consciousness' :
              node.status === 'processing' ? 'bg-accent-gold border-accent-gold' :
              'bg-trinity-guardian border-trinity-guardian'
            } ${selectedNode === node.id ? 'scale-125 shadow-lg' : 'hover:scale-110'}`}
            style={{ left: node.x, top: node.y }}
            onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
          >
            <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs whitespace-nowrap">
              {node.id}
            </div>
          </div>
        ))}
      </div>
      {selectedNode && (
        <div className="mt-4 p-3 bg-black/50 rounded border border-white/10">
          <h4 className="font-mono text-sm text-trinity-consciousness">{selectedNode}</h4>
          <div className="mt-2 text-xs space-y-1">
            <div>Type: {nodes.find(n => n.id === selectedNode)?.type}</div>
            <div>Status: {nodes.find(n => n.id === selectedNode)?.status}</div>
            <div>Last Update: 2.3s ago</div>
            <div>Memory Usage: 15.7MB</div>
          </div>
        </div>
      )}
    </div>
  )
}

// Memory Viewer Component
const MemoryViewer = () => {
  const [selectedFold, setSelectedFold] = useState(0)

  const folds = [
    { id: 0, timestamp: '14:32:15', event: 'Node initialization', weight: 0.8, connections: 3 },
    { id: 1, timestamp: '14:32:18', event: 'Math calculation', weight: 0.6, connections: 2 },
    { id: 2, timestamp: '14:32:22', event: 'Validation complete', weight: 0.9, connections: 4 },
    { id: 3, timestamp: '14:32:25', event: 'Memory consolidation', weight: 0.7, connections: 1 },
  ]

  return (
    <div className="h-full glass-panel rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-regular text-sm tracking-widest uppercase">Memory Folds</h3>
        <div className="text-xs text-white/60">
          Active: {folds.length} | Capacity: 1000
        </div>
      </div>
      <div className="space-y-2 max-h-80 overflow-y-auto">
        {folds.map((fold) => (
          <div
            key={fold.id}
            className={`p-3 rounded border cursor-pointer transition-all ${
              selectedFold === fold.id 
                ? 'border-trinity-consciousness bg-trinity-consciousness/10' 
                : 'border-white/10 hover:border-white/20'
            }`}
            onClick={() => setSelectedFold(fold.id)}
          >
            <div className="flex items-center justify-between">
              <div className="font-mono text-sm">{fold.event}</div>
              <div className="text-xs text-white/60">{fold.timestamp}</div>
            </div>
            <div className="mt-2 flex items-center space-x-4 text-xs">
              <div>Weight: {fold.weight}</div>
              <div>Connections: {fold.connections}</div>
              <div className="flex-1">
                <div className="w-full bg-white/10 rounded-full h-1">
                  <div 
                    className="bg-trinity-consciousness h-1 rounded-full"
                    style={{ width: `${fold.weight * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {selectedFold !== null && (
        <div className="mt-4 p-3 bg-black/50 rounded border border-white/10">
          <h4 className="font-mono text-sm text-trinity-consciousness mb-2">Fold Details</h4>
          <div className="text-xs space-y-1">
            <div>Causal Chain: Preserved</div>
            <div>Emotional Context: Neutral</div>
            <div>Decay Rate: 0.02%/hour</div>
            <div>Retrieval Score: 0.95</div>
          </div>
        </div>
      )}
    </div>
  )
}

// Guardian Metrics Component
const GuardianMetrics = () => {
  const metrics = [
    { label: 'Ethics Score', value: 0.97, target: 0.95, color: 'trinity-guardian' },
    { label: 'Drift Detection', value: 0.03, target: 0.15, color: 'trinity-consciousness' },
    { label: 'Trust Level', value: 0.94, target: 0.90, color: 'trinity-identity' },
    { label: 'Repair Efficiency', value: 0.99, target: 0.95, color: 'accent-gold' },
  ]

  return (
    <div className="h-full glass-panel rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-regular text-sm tracking-widest uppercase">Guardian Metrics</h3>
        <div className="text-xs text-trinity-guardian">🛡️ ACTIVE</div>
      </div>
      <div className="space-y-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>{metric.label}</span>
              <span className={`text-${metric.color}`}>
                {(metric.value * 100).toFixed(1)}%
              </span>
            </div>
            <div className="relative">
              <div className="w-full bg-white/10 rounded-full h-2">
                <div 
                  className={`bg-${metric.color} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${metric.value * 100}%` }}
                ></div>
              </div>
              <div 
                className="absolute top-0 w-0.5 h-2 bg-white/50"
                style={{ left: `${metric.target * 100}%` }}
                title={`Target: ${(metric.target * 100).toFixed(1)}%`}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 p-3 bg-black/50 rounded border border-white/10">
        <h4 className="font-mono text-sm text-trinity-guardian mb-2">Recent Actions</h4>
        <div className="text-xs space-y-1">
          <div className="flex justify-between">
            <span>Ethical boundary check</span>
            <span className="text-white/60">2s ago</span>
          </div>
          <div className="flex justify-between">
            <span>Drift correction applied</span>
            <span className="text-white/60">15s ago</span>
          </div>
          <div className="flex justify-between">
            <span>Trust validation passed</span>
            <span className="text-white/60">1m ago</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// System Logs Component
const SystemLogs = () => {
  const logs = [
    { timestamp: '14:32:28', level: 'INFO', source: 'Guardian', message: 'Ethics validation passed for node fact_001' },
    { timestamp: '14:32:25', level: 'DEBUG', source: 'Memory', message: 'Fold consolidation completed: 4 folds processed' },
    { timestamp: '14:32:22', level: 'INFO', source: 'Validator', message: 'Math calculation validated: result within bounds' },
    { timestamp: '14:32:18', level: 'WARN', source: 'Network', message: 'Connection latency increased: 150ms -> 180ms' },
    { timestamp: '14:32:15', level: 'INFO', source: 'System', message: 'Node initialization complete: all systems online' },
  ]

  return (
    <div className="h-full glass-panel rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-regular text-sm tracking-widest uppercase">System Logs</h3>
        <div className="flex items-center space-x-2">
          <button className="text-xs px-2 py-1 bg-white/10 rounded">Clear</button>
          <button className="text-xs px-2 py-1 bg-white/10 rounded">Export</button>
        </div>
      </div>
      <div className="space-y-1 max-h-80 overflow-y-auto font-mono text-xs">
        {logs.map((log, i) => (
          <div key={i} className="flex items-start space-x-3 py-1">
            <span className="text-white/60 shrink-0">{log.timestamp}</span>
            <span className={`shrink-0 ${
              log.level === 'ERROR' ? 'text-red-400' :
              log.level === 'WARN' ? 'text-yellow-400' :
              log.level === 'INFO' ? 'text-trinity-consciousness' :
              'text-white/60'
            }`}>
              {log.level}
            </span>
            <span className="text-trinity-guardian shrink-0">{log.source}</span>
            <span className="text-white/80">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// API Tester Component
const ApiTester = () => {
  const [endpoint, setEndpoint] = useState('/api/nodes/status')
  const [method, setMethod] = useState('GET')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  const handleTest = async () => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      const mockResponse = {
        status: 'success',
        data: {
          nodes: 4,
          active: 3,
          memory_usage: '15.7MB',
          uptime: '4h 23m'
        },
        timestamp: new Date().toISOString()
      }
      setResponse(JSON.stringify(mockResponse, null, 2))
      setLoading(false)
    }, 1000)
  }

  return (
    <div className="h-full glass-panel rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-regular text-sm tracking-widest uppercase">API Tester</h3>
        <div className="text-xs text-white/60">Base URL: localhost:8080</div>
      </div>
      <div className="space-y-4">
        <div className="flex space-x-2">
          <select 
            value={method} 
            onChange={(e) => setMethod(e.target.value)}
            className="px-3 py-2 bg-black/50 border border-white/10 rounded text-sm"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
          <input
            type="text"
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            className="flex-1 px-3 py-2 bg-black/50 border border-white/10 rounded text-sm"
            placeholder="/api/endpoint"
          />
          <button
            onClick={handleTest}
            disabled={loading}
            className="px-4 py-2 bg-trinity-consciousness text-primary-dark rounded text-sm hover:opacity-90 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test'}
          </button>
        </div>
        <div className="h-64">
          <div className="text-xs text-white/60 mb-2">Response:</div>
          <pre className="h-full p-3 bg-black/50 border border-white/10 rounded overflow-auto text-xs font-mono">
            {response || 'No response yet. Click "Test" to send a request.'}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default function ConsolePage() {
  const [activeTab, setActiveTab] = useState('terminal')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [showCommandPalette, setShowCommandPalette] = useState(false)

  const tabs: TabConfig[] = [
    { id: 'terminal', label: 'Terminal', icon: <TerminalIcon />, component: <Terminal /> },
    { id: 'nodes', label: 'Node Graph', icon: <NetworkIcon />, component: <NodeGraph /> },
    { id: 'memory', label: 'Memory Folds', icon: <MemoryIcon />, component: <MemoryViewer /> },
    { id: 'guardian', label: 'Guardian', icon: <ShieldIcon />, component: <GuardianMetrics /> },
    { id: 'logs', label: 'Logs', icon: <LogsIcon />, component: <SystemLogs /> },
    { id: 'api', label: 'API Tester', icon: <ApiIcon />, component: <ApiTester /> },
  ]

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        if (e.key === 'k') {
          e.preventDefault()
          setShowCommandPalette(true)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="min-h-screen bg-primary-dark text-primary-light">
      {/* Header */}
      <div className="h-16 glass-panel border-b border-white/10 flex items-center justify-between px-6">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-ultralight tracking-widest gradient-text">
            MATADA CONSOLE
          </h1>
          <div className="flex items-center space-x-2 text-xs">
            <div className="w-2 h-2 rounded-full bg-trinity-guardian animate-pulse"></div>
            <span>System Online</span>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-xs text-white/60">
            Press <kbd className="px-2 py-1 bg-white/10 rounded">⌘K</kbd> for command palette
          </div>
          <button
            onClick={() => setShowCommandPalette(true)}
            className="p-2 hover:bg-white/10 rounded"
          >
            <SearchIcon />
          </button>
        </div>
      </div>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} glass-panel border-r border-white/10 transition-all duration-300`}>
          <div className="p-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="w-full flex items-center justify-between p-2 hover:bg-white/10 rounded"
            >
              {!sidebarCollapsed && <span className="font-regular text-sm tracking-widest uppercase">Navigation</span>}
              <div className="w-4 h-4">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d={sidebarCollapsed ? "M9 5l7 7-7 7" : "M15 19l-7-7 7-7"} />
                </svg>
              </div>
            </button>
          </div>
          <nav className="px-4 space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 p-3 rounded transition-all ${
                  activeTab === tab.id 
                    ? 'bg-trinity-consciousness/20 text-trinity-consciousness' 
                    : 'hover:bg-white/10'
                }`}
              >
                {tab.icon}
                {!sidebarCollapsed && (
                  <span className="font-regular text-sm tracking-wider uppercase">
                    {tab.label}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Tab Header */}
          <div className="h-12 border-b border-white/10 flex items-center px-6">
            <div className="flex items-center space-x-2">
              {tabs.find(t => t.id === activeTab)?.icon}
              <span className="font-regular text-sm tracking-widest uppercase">
                {tabs.find(t => t.id === activeTab)?.label}
              </span>
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="h-full"
              >
                {tabs.find(t => t.id === activeTab)?.component}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="h-8 bg-black/50 border-t border-white/10 flex items-center justify-between px-6 text-xs">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-trinity-consciousness"></div>
            <span>MATADA v1.0.0</span>
          </div>
          <div>Uptime: 4h 23m</div>
          <div>Memory: 15.7MB</div>
        </div>
        <div className="flex items-center space-x-4">
          <div>Trinity Framework: ⚛️🧠🛡️</div>
          <div>Drift: 0.03</div>
          <div>Ethics: 0.97</div>
        </div>
      </div>

      {/* Command Palette */}
      <AnimatePresence>
        {showCommandPalette && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center pt-32">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -20 }}
              className="w-96 glass-panel rounded-lg border border-white/20 p-4"
            >
              <div className="flex items-center space-x-2 mb-4">
                <SearchIcon />
                <input
                  type="text"
                  placeholder="Search commands..."
                  className="flex-1 bg-transparent outline-none text-sm"
                  autoFocus
                />
              </div>
              <div className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id)
                      setShowCommandPalette(false)
                    }}
                    className="w-full flex items-center space-x-3 p-2 hover:bg-white/10 rounded text-left"
                  >
                    {tab.icon}
                    <span className="text-sm">{tab.label}</span>
                  </button>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-white/10 text-xs text-white/60">
                Press <kbd className="px-1 py-0.5 bg-white/10 rounded">Esc</kbd> to close
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Close command palette on Escape */}
      {showCommandPalette && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowCommandPalette(false)}
          onKeyDown={(e) => e.key === 'Escape' && setShowCommandPalette(false)}
        />
      )}
    </div>
  )
}