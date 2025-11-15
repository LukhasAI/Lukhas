import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  Footer,
  FooterSection,
  FooterLink,
} from './Footer'

describe('Footer', () => {
  it('renders children correctly', () => {
    render(<Footer>Footer Content</Footer>)
    expect(screen.getByText('Footer Content')).toBeInTheDocument()
  })

  it('renders as footer element', () => {
    const { container } = render(<Footer>Footer</Footer>)
    expect(container.querySelector('footer')).toBeInTheDocument()
  })

  describe('Glassmorphism', () => {
    it('does not apply glassmorphism by default', () => {
      const { container } = render(<Footer>Footer</Footer>)
      const footer = container.querySelector('footer')
      expect(footer).toHaveClass('bg-deep-space', 'border-border')
      expect(footer).not.toHaveClass('bg-glass')
    })

    it('applies glassmorphism when enabled', () => {
      const { container } = render(<Footer glass>Footer</Footer>)
      const footer = container.querySelector('footer')
      expect(footer).toHaveClass('bg-glass', 'backdrop-blur-glass', 'border-glass-border')
    })
  })

  describe('Ecosystem Navigation', () => {
    it('shows ecosystem navigation by default', () => {
      render(<Footer>Footer</Footer>)
      expect(screen.getByText('LUKHAS Ecosystem')).toBeInTheDocument()
      expect(screen.getByText('lukhas.id')).toBeInTheDocument()
      expect(screen.getByText('lukhas.com')).toBeInTheDocument()
      expect(screen.getByText('lukhas.us')).toBeInTheDocument()
    })

    it('hides ecosystem navigation when disabled', () => {
      render(<Footer showEcosystem={false}>Footer</Footer>)
      expect(screen.queryByText('LUKHAS Ecosystem')).not.toBeInTheDocument()
      expect(screen.queryByText('lukhas.id')).not.toBeInTheDocument()
    })

    it('renders ecosystem links with correct hrefs', () => {
      render(<Footer>Footer</Footer>)

      const idLink = screen.getByText('lukhas.id').closest('a')
      const comLink = screen.getByText('lukhas.com').closest('a')
      const usLink = screen.getByText('lukhas.us').closest('a')

      expect(idLink).toHaveAttribute('href', 'https://lukhas.id')
      expect(comLink).toHaveAttribute('href', 'https://lukhas.com')
      expect(usLink).toHaveAttribute('href', 'https://lukhas.us')
    })

    it('renders ecosystem descriptions', () => {
      render(<Footer>Footer</Footer>)
      expect(screen.getByText('Identity & Authentication')).toBeInTheDocument()
      expect(screen.getByText('Platform & Products')).toBeInTheDocument()
      expect(screen.getByText('Compliance & Governance')).toBeInTheDocument()
    })
  })

  describe('Footer Bottom', () => {
    it('renders copyright with current year', () => {
      render(<Footer>Footer</Footer>)
      const currentYear = new Date().getFullYear()
      expect(screen.getByText(`© ${currentYear} LUKHAS AI. All rights reserved.`)).toBeInTheDocument()
    })

    it('renders legal links', () => {
      render(<Footer>Footer</Footer>)
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument()
      expect(screen.getByText('Terms of Service')).toBeInTheDocument()
      expect(screen.getByText('Security')).toBeInTheDocument()
    })

    it('renders legal links with correct hrefs', () => {
      render(<Footer>Footer</Footer>)

      const privacyLink = screen.getByText('Privacy Policy')
      const termsLink = screen.getByText('Terms of Service')
      const securityLink = screen.getByText('Security')

      expect(privacyLink).toHaveAttribute('href', '/privacy')
      expect(termsLink).toHaveAttribute('href', '/terms')
      expect(securityLink).toHaveAttribute('href', '/security')
    })
  })

  it('merges custom className', () => {
    const { container } = render(<Footer className="custom-footer">Footer</Footer>)
    const footer = container.querySelector('footer')
    expect(footer).toHaveClass('custom-footer')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<Footer ref={ref}>Footer</Footer>)
    expect(ref.current).toBeInstanceOf(HTMLElement)
  })
})

describe('FooterSection', () => {
  it('renders title and children correctly', () => {
    render(
      <FooterSection title="Product">
        <a>Features</a>
        <a>Pricing</a>
      </FooterSection>
    )

    expect(screen.getByText('Product')).toBeInTheDocument()
    expect(screen.getByText('Features')).toBeInTheDocument()
    expect(screen.getByText('Pricing')).toBeInTheDocument()
  })

  it('applies LUKHAS typography to title', () => {
    render(<FooterSection title="Section">Content</FooterSection>)
    const title = screen.getByText('Section')
    expect(title).toHaveClass('text-sm', 'font-light', 'uppercase', 'tracking-logo')
  })

  it('applies column flex layout', () => {
    const { container } = render(<FooterSection title="Test">Content</FooterSection>)
    expect(container.firstChild).toHaveClass('flex', 'flex-col', 'gap-3')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<FooterSection ref={ref} title="Test">Content</FooterSection>)
    expect(ref.current).toBeInstanceOf(HTMLDivElement)
  })
})

describe('FooterLink', () => {
  it('renders children correctly', () => {
    render(<FooterLink href="/about">About Us</FooterLink>)
    expect(screen.getByText('About Us')).toBeInTheDocument()
  })

  it('renders as anchor element with href', () => {
    render(<FooterLink href="/contact">Contact</FooterLink>)
    const link = screen.getByText('Contact')
    expect(link.tagName).toBe('A')
    expect(link).toHaveAttribute('href', '/contact')
  })

  it('applies secondary text color', () => {
    const { container } = render(<FooterLink href="/">Link</FooterLink>)
    const link = container.firstChild as HTMLElement
    expect(link).toHaveClass('text-text-secondary', 'hover:text-lambda-blue')
  })

  it('merges custom className', () => {
    const { container } = render(<FooterLink className="custom-link" href="/">Link</FooterLink>)
    expect(container.firstChild).toHaveClass('custom-link')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<FooterLink ref={ref} href="/">Link</FooterLink>)
    expect(ref.current).toBeInstanceOf(HTMLAnchorElement)
  })
})

describe('Footer Full Composition', () => {
  it('renders full footer composition correctly', () => {
    render(
      <Footer glass showEcosystem>
        <FooterSection title="Product">
          <FooterLink href="/features">Features</FooterLink>
          <FooterLink href="/pricing">Pricing</FooterLink>
        </FooterSection>
        <FooterSection title="Company">
          <FooterLink href="/about">About</FooterLink>
          <FooterLink href="/careers">Careers</FooterLink>
        </FooterSection>
        <FooterSection title="Resources">
          <FooterLink href="/docs">Documentation</FooterLink>
          <FooterLink href="/blog">Blog</FooterLink>
        </FooterSection>
        <FooterSection title="Legal">
          <FooterLink href="/privacy">Privacy</FooterLink>
          <FooterLink href="/terms">Terms</FooterLink>
        </FooterSection>
      </Footer>
    )

    // Check ecosystem nav
    expect(screen.getByText('LUKHAS Ecosystem')).toBeInTheDocument()

    // Check all sections
    expect(screen.getByText('Product')).toBeInTheDocument()
    expect(screen.getByText('Company')).toBeInTheDocument()
    expect(screen.getByText('Resources')).toBeInTheDocument()
    expect(screen.getByText('Legal')).toBeInTheDocument()

    // Check all links
    expect(screen.getByText('Features')).toBeInTheDocument()
    expect(screen.getByText('About')).toBeInTheDocument()
    expect(screen.getByText('Documentation')).toBeInTheDocument()

    // Check footer bottom
    const currentYear = new Date().getFullYear()
    expect(screen.getByText(`© ${currentYear} LUKHAS AI. All rights reserved.`)).toBeInTheDocument()
  })

  it('applies responsive grid layout', () => {
    const { container } = render(
      <Footer>
        <FooterSection title="Section">Link</FooterSection>
      </Footer>
    )

    // Find the main footer grid (there are two grids: ecosystem and main footer)
    const grids = container.querySelectorAll('.grid')
    const footerGrid = grids[1] // Second grid is the main footer grid
    expect(footerGrid).toBeInTheDocument()
    expect(footerGrid).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
  })
})
