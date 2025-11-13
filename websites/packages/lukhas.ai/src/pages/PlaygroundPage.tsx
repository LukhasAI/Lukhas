import {  Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Button } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import NeuralBackground from '../components/NeuralBackground'
import ConstellationPulse from '../components/playground/ConstellationPulse'
import ChatInterface from '../components/playground/ChatInterface'
import ControlBar from '../components/playground/ControlBar'

export default function PlaygroundPage() {
  return (
    <div className="min-h-screen bg-black flex flex-col">
      {/* Neural Network Background (slightly brighter for playground) */}
      <div className="fixed inset-0 z-0">
        <NeuralBackground />
      </div>

      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-black/70 backdrop-blur-md border-b border-white/5">
        <HeaderLogo href="/">
          <span className="text-2xl tracking-[0.15em] text-white" style={{ fontFamily: "'Helvetica Neue', -apple-system, BlinkMacSystemFont, sans-serif", fontWeight: 100 }}>
            LUKHAS
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="/technology">Technology</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <Link to="/">
            <Button variant="ghost">
              Home
            </Button>
          </Link>
        </HeaderActions>
      </Header>

      {/* Main Playground Layout */}
      <div className="flex-1 flex pt-16 relative z-10">
        {/* Left Sidebar - Constellation Pulse */}
        <ConstellationPulse />

        {/* Main Content - Control Bar + Chat Interface */}
        <div className="flex-1 flex flex-col">
          <ControlBar />
          <ChatInterface />
        </div>
      </div>
    </div>
  )
}
