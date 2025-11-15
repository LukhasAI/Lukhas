import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import {
  GlassCard,
  GlassCardHeader,
  GlassCardTitle,
  GlassCardDescription,
  GlassCardContent,
  GlassCardFooter,
} from './GlassCard'

describe('GlassCard', () => {
  it('renders children correctly', () => {
    render(<GlassCard>Test Content</GlassCard>)
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies default variant styles', () => {
    const { container } = render(<GlassCard>Content</GlassCard>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('bg-glass')
  })

  it('applies elevated variant styles', () => {
    const { container } = render(<GlassCard variant="elevated">Content</GlassCard>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('bg-card-elevated')
  })

  it('applies interactive variant styles', () => {
    const { container } = render(<GlassCard variant="interactive">Content</GlassCard>)
    const card = container.firstChild as HTMLElement
    expect(card).toHaveClass('cursor-pointer')
  })

  it('applies domain accent borders correctly', () => {
    const { container: idContainer } = render(<GlassCard domainAccent="id">ID</GlassCard>)
    expect(idContainer.firstChild).toHaveClass('border-l-domain-id-purple')

    const { container: comContainer } = render(<GlassCard domainAccent="com">COM</GlassCard>)
    expect(comContainer.firstChild).toHaveClass('border-l-domain-com-trust-blue')

    const { container: usContainer } = render(<GlassCard domainAccent="us">US</GlassCard>)
    expect(usContainer.firstChild).toHaveClass('border-l-domain-us-institutional')
  })

  it('applies hoverable styles by default', () => {
    const { container } = render(<GlassCard>Content</GlassCard>)
    expect(container.firstChild).toHaveClass('hover:-translate-y-1')
  })

  it('does not apply hoverable styles when disabled', () => {
    const { container } = render(<GlassCard hoverable={false}>Content</GlassCard>)
    expect(container.firstChild).not.toHaveClass('hover:-translate-y-1')
  })

  it('applies breathing animation when enabled', () => {
    const { container } = render(<GlassCard breathe>Content</GlassCard>)
    expect(container.firstChild).toHaveClass('animate-breathe-subtle')
  })

  it('merges custom className', () => {
    const { container } = render(<GlassCard className="custom-class">Content</GlassCard>)
    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<GlassCard ref={ref}>Content</GlassCard>)
    expect(ref.current).toBeInstanceOf(HTMLDivElement)
  })
})

describe('GlassCardHeader', () => {
  it('renders children correctly', () => {
    render(<GlassCardHeader>Header Content</GlassCardHeader>)
    expect(screen.getByText('Header Content')).toBeInTheDocument()
  })

  it('applies default margin bottom', () => {
    const { container } = render(<GlassCardHeader>Header</GlassCardHeader>)
    expect(container.firstChild).toHaveClass('mb-4')
  })
})

describe('GlassCardTitle', () => {
  it('renders as h3 element', () => {
    render(<GlassCardTitle>Title</GlassCardTitle>)
    const title = screen.getByText('Title')
    expect(title.tagName).toBe('H3')
  })

  it('applies LUKHAS typography styles', () => {
    const { container } = render(<GlassCardTitle>Title</GlassCardTitle>)
    const title = container.firstChild as HTMLElement
    expect(title).toHaveClass('text-2xl', 'font-light', 'uppercase', 'tracking-logo', 'text-lambda-blue')
  })
})

describe('GlassCardDescription', () => {
  it('renders as paragraph element', () => {
    render(<GlassCardDescription>Description</GlassCardDescription>)
    const desc = screen.getByText('Description')
    expect(desc.tagName).toBe('P')
  })

  it('applies secondary text color', () => {
    const { container } = render(<GlassCardDescription>Text</GlassCardDescription>)
    expect(container.firstChild).toHaveClass('text-text-secondary')
  })
})

describe('GlassCardContent', () => {
  it('renders children correctly', () => {
    render(<GlassCardContent>Content</GlassCardContent>)
    expect(screen.getByText('Content')).toBeInTheDocument()
  })

  it('applies primary text color', () => {
    const { container } = render(<GlassCardContent>Content</GlassCardContent>)
    expect(container.firstChild).toHaveClass('text-text-primary')
  })
})

describe('GlassCardFooter', () => {
  it('renders children correctly', () => {
    render(<GlassCardFooter>Footer</GlassCardFooter>)
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })

  it('applies flex layout with gap', () => {
    const { container } = render(<GlassCardFooter>Footer</GlassCardFooter>)
    expect(container.firstChild).toHaveClass('flex', 'items-center', 'gap-2')
  })

  it('applies top margin', () => {
    const { container } = render(<GlassCardFooter>Footer</GlassCardFooter>)
    expect(container.firstChild).toHaveClass('mt-6')
  })
})

describe('GlassCard Full Composition', () => {
  it('renders full card composition correctly', () => {
    render(
      <GlassCard domainAccent="id">
        <GlassCardHeader>
          <GlassCardTitle>Identity Management</GlassCardTitle>
          <GlassCardDescription>Secure authentication</GlassCardDescription>
        </GlassCardHeader>
        <GlassCardContent>Main content here</GlassCardContent>
        <GlassCardFooter>
          <button>Action</button>
        </GlassCardFooter>
      </GlassCard>
    )

    expect(screen.getByText('Identity Management')).toBeInTheDocument()
    expect(screen.getByText('Secure authentication')).toBeInTheDocument()
    expect(screen.getByText('Main content here')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument()
  })
})
