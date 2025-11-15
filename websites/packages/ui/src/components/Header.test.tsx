import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  Header,
  HeaderLogo,
  HeaderNav,
  HeaderNavLink,
  HeaderActions,
} from './Header'

describe('Header', () => {
  it('renders children correctly', () => {
    render(<Header>Header Content</Header>)
    expect(screen.getByText('Header Content')).toBeInTheDocument()
  })

  it('renders as header element', () => {
    const { container } = render(<Header>Header</Header>)
    expect(container.querySelector('header')).toBeInTheDocument()
  })

  describe('Sticky Positioning', () => {
    it('applies sticky positioning by default', () => {
      const { container } = render(<Header>Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('sticky', 'top-0', 'z-fixed')
    })

    it('does not apply sticky positioning when disabled', () => {
      const { container } = render(<Header sticky={false}>Header</Header>)
      const header = container.querySelector('header')
      expect(header).not.toHaveClass('sticky')
    })
  })

  describe('Glassmorphism', () => {
    it('applies glassmorphism by default', () => {
      const { container } = render(<Header>Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('bg-glass', 'backdrop-blur-glass', 'border-glass-border')
    })

    it('does not apply glassmorphism when disabled', () => {
      const { container } = render(<Header glass={false}>Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('bg-deep-space', 'border-border')
      expect(header).not.toHaveClass('bg-glass')
    })
  })

  describe('Domain Accents', () => {
    it('applies identity purple accent', () => {
      const { container } = render(<Header domain="id">Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('border-b-domain-id-purple/30')
    })

    it('applies commercial blue accent', () => {
      const { container } = render(<Header domain="com">Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('border-b-domain-com-trust-blue/30')
    })

    it('applies institutional accent', () => {
      const { container } = render(<Header domain="us">Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('border-b-domain-us-institutional/30')
    })

    it('does not apply domain accent by default', () => {
      const { container } = render(<Header>Header</Header>)
      const header = container.querySelector('header')
      expect(header).not.toHaveClass('border-b-domain-id-purple/30')
    })
  })

  describe('Breathing Animation', () => {
    it('applies breathing animation when enabled', () => {
      const { container } = render(<Header breathe>Header</Header>)
      const header = container.querySelector('header')
      expect(header).toHaveClass('animate-breathe-subtle')
    })

    it('does not apply breathing animation by default', () => {
      const { container } = render(<Header>Header</Header>)
      const header = container.querySelector('header')
      expect(header).not.toHaveClass('animate-breathe-subtle')
    })
  })

  it('merges custom className', () => {
    const { container } = render(<Header className="custom-header">Header</Header>)
    const header = container.querySelector('header')
    expect(header).toHaveClass('custom-header')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<Header ref={ref}>Header</Header>)
    expect(ref.current).toBeInstanceOf(HTMLElement)
  })
})

describe('HeaderLogo', () => {
  it('renders children correctly', () => {
    render(<HeaderLogo>LUKHAS</HeaderLogo>)
    expect(screen.getByText('LUKHAS')).toBeInTheDocument()
  })

  it('applies LUKHAS typography styles', () => {
    render(<HeaderLogo>LUKHAS</HeaderLogo>)
    const logo = screen.getByText('LUKHAS')
    expect(logo).toHaveClass('text-2xl', 'font-thin', 'uppercase', 'tracking-thin-capitals')
  })

  it('renders as link when href is provided', () => {
    render(<HeaderLogo href="/home">LUKHAS</HeaderLogo>)
    const link = screen.getByText('LUKHAS').closest('a')
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/home')
  })

  it('uses default href "/" when not specified', () => {
    render(<HeaderLogo>LUKHAS</HeaderLogo>)
    const link = screen.getByText('LUKHAS').closest('a')
    expect(link).toHaveAttribute('href', '/')
  })

  it('merges custom className', () => {
    const { container } = render(<HeaderLogo className="custom-logo">LUKHAS</HeaderLogo>)
    expect(container.querySelector('a')).toHaveClass('custom-logo')
  })
})

describe('HeaderNav', () => {
  it('renders children correctly', () => {
    render(
      <HeaderNav>
        <a>Link 1</a>
        <a>Link 2</a>
      </HeaderNav>
    )

    expect(screen.getByText('Link 1')).toBeInTheDocument()
    expect(screen.getByText('Link 2')).toBeInTheDocument()
  })

  it('renders as nav element', () => {
    const { container } = render(<HeaderNav>Nav</HeaderNav>)
    expect(container.querySelector('nav')).toBeInTheDocument()
  })

  it('applies flex layout with gap', () => {
    const { container } = render(<HeaderNav>Nav</HeaderNav>)
    const nav = container.querySelector('nav')
    expect(nav).toHaveClass('flex', 'items-center', 'gap-6')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<HeaderNav ref={ref}>Nav</HeaderNav>)
    expect(ref.current).toBeInstanceOf(HTMLElement)
  })
})

describe('HeaderNavLink', () => {
  it('renders children correctly', () => {
    render(<HeaderNavLink href="/about">About</HeaderNavLink>)
    expect(screen.getByText('About')).toBeInTheDocument()
  })

  it('renders as anchor element', () => {
    render(<HeaderNavLink href="/test">Test</HeaderNavLink>)
    const link = screen.getByText('Test')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/test')
  })

  it('applies LUKHAS typography styles', () => {
    const { container } = render(<HeaderNavLink href="/">Link</HeaderNavLink>)
    const link = container.firstChild as HTMLElement
    expect(link).toHaveClass('text-sm', 'font-light', 'uppercase', 'tracking-logo')
  })

  it('applies active state styles', () => {
    const { container } = render(<HeaderNavLink active href="/">Active</HeaderNavLink>)
    const link = container.firstChild as HTMLElement
    expect(link).toHaveClass('text-lambda-blue')
  })

  it('applies inactive state styles by default', () => {
    const { container } = render(<HeaderNavLink href="/">Inactive</HeaderNavLink>)
    const link = container.firstChild as HTMLElement
    expect(link).toHaveClass('text-text-secondary')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<HeaderNavLink ref={ref} href="/">Link</HeaderNavLink>)
    expect(ref.current).toBeInstanceOf(HTMLAnchorElement)
  })
})

describe('HeaderActions', () => {
  it('renders children correctly', () => {
    render(
      <HeaderActions>
        <button>Action 1</button>
        <button>Action 2</button>
      </HeaderActions>
    )

    expect(screen.getByText('Action 1')).toBeInTheDocument()
    expect(screen.getByText('Action 2')).toBeInTheDocument()
  })

  it('applies flex layout with gap', () => {
    const { container } = render(<HeaderActions>Actions</HeaderActions>)
    expect(container.firstChild).toHaveClass('flex', 'items-center', 'gap-3')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<HeaderActions ref={ref}>Actions</HeaderActions>)
    expect(ref.current).toBeInstanceOf(HTMLDivElement)
  })
})

describe('Header Full Composition', () => {
  it('renders full header composition correctly', () => {
    render(
      <Header domain="id" glass sticky>
        <HeaderLogo href="/">LUKHAS</HeaderLogo>
        <HeaderNav>
          <HeaderNavLink active href="/">
            Home
          </HeaderNavLink>
          <HeaderNavLink href="/features">Features</HeaderNavLink>
          <HeaderNavLink href="/pricing">Pricing</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <button>Sign In</button>
          <button>Sign Up</button>
        </HeaderActions>
      </Header>
    )

    expect(screen.getByText('LUKHAS')).toBeInTheDocument()
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Features')).toBeInTheDocument()
    expect(screen.getByText('Pricing')).toBeInTheDocument()
    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
  })

  it('applies responsive container', () => {
    const { container } = render(<Header>Header</Header>)
    const contentContainer = container.querySelector('.container')
    expect(contentContainer).toBeInTheDocument()
    expect(contentContainer).toHaveClass('mx-auto')
  })
})
