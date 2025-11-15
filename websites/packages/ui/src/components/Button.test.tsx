import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button, ButtonGroup } from './Button'

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click Me</Button>)
    expect(screen.getByText('Click Me')).toBeInTheDocument()
  })

  it('renders as button element', () => {
    render(<Button>Click</Button>)
    const button = screen.getByRole('button')
    expect(button.tagName).toBe('BUTTON')
  })

  describe('Variants', () => {
    it('applies default variant styles', () => {
      const { container } = render(<Button>Default</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('bg-glass', 'backdrop-blur-glass')
    })

    it('applies primary variant styles', () => {
      const { container } = render(<Button variant="primary">Primary</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('bg-lambda-blue', 'text-deep-space')
    })

    it('applies secondary variant styles', () => {
      const { container } = render(<Button variant="secondary">Secondary</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('bg-card-elevated')
    })

    it('applies ghost variant styles', () => {
      const { container } = render(<Button variant="ghost">Ghost</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('text-text-primary', 'hover:bg-glass')
    })

    it('applies outline variant styles', () => {
      const { container } = render(<Button variant="outline">Outline</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('border-lambda-blue', 'text-lambda-blue')
    })

    it('applies destructive variant styles', () => {
      const { container } = render(<Button variant="destructive">Delete</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('bg-danger')
    })
  })

  describe('Sizes', () => {
    it('applies small size styles', () => {
      const { container } = render(<Button size="sm">Small</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('h-9', 'px-4', 'text-xs')
    })

    it('applies medium size styles by default', () => {
      const { container } = render(<Button>Medium</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('h-11', 'px-6', 'text-sm')
    })

    it('applies large size styles', () => {
      const { container } = render(<Button size="lg">Large</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('h-14', 'px-8', 'text-base')
    })

    it('applies icon size styles', () => {
      const { container } = render(<Button size="icon">+</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('h-11', 'w-11')
    })
  })

  describe('Glow Effect', () => {
    it('applies glow effect on primary variant when enabled', () => {
      const { container } = render(<Button variant="primary" glow>Glow</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('hover:shadow-glow-blue')
    })

    it('applies glow effect on outline variant when enabled', () => {
      const { container } = render(<Button variant="outline" glow>Glow</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('hover:shadow-glow-blue')
    })

    it('does not apply glow effect by default', () => {
      const { container } = render(<Button variant="primary">No Glow</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).not.toHaveClass('hover:shadow-glow-blue')
    })
  })

  describe('Full Width', () => {
    it('applies full width when enabled', () => {
      const { container } = render(<Button fullWidth>Full Width</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('w-full')
    })

    it('does not apply full width by default', () => {
      const { container } = render(<Button>Normal</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).not.toHaveClass('w-full')
    })
  })

  describe('Loading State', () => {
    it('shows loading spinner when isLoading is true', () => {
      const { container } = render(<Button isLoading>Loading</Button>)
      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
      expect(svg).toHaveClass('animate-spin')
    })

    it('disables button when isLoading is true', () => {
      render(<Button isLoading>Loading</Button>)
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
    })

    it('does not show loading spinner by default', () => {
      const { container } = render(<Button>Not Loading</Button>)
      const svg = container.querySelector('svg')
      expect(svg).not.toBeInTheDocument()
    })
  })

  describe('Disabled State', () => {
    it('disables button when disabled prop is true', () => {
      render(<Button disabled>Disabled</Button>)
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
    })

    it('applies disabled styles', () => {
      const { container } = render(<Button disabled>Disabled</Button>)
      const button = container.firstChild as HTMLElement
      expect(button).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50')
    })
  })

  describe('Click Handling', () => {
    it('calls onClick handler when clicked', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click Me</Button>)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('does not call onClick when disabled', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      render(<Button disabled onClick={handleClick}>Disabled</Button>)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(handleClick).not.toHaveBeenCalled()
    })

    it('does not call onClick when loading', async () => {
      const user = userEvent.setup()
      const handleClick = vi.fn()
      render(<Button isLoading onClick={handleClick}>Loading</Button>)

      const button = screen.getByRole('button')
      await user.click(button)

      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Custom Props', () => {
    it('merges custom className', () => {
      const { container } = render(<Button className="custom-class">Custom</Button>)
      expect(container.firstChild).toHaveClass('custom-class')
    })

    it('forwards ref correctly', () => {
      const ref = { current: null }
      render(<Button ref={ref}>Button</Button>)
      expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    })

    it('passes through HTML button attributes', () => {
      render(<Button type="submit" data-testid="submit-btn">Submit</Button>)
      const button = screen.getByTestId('submit-btn')
      expect(button).toHaveAttribute('type', 'submit')
    })
  })
})

describe('ButtonGroup', () => {
  it('renders children correctly', () => {
    render(
      <ButtonGroup>
        <Button>Button 1</Button>
        <Button>Button 2</Button>
      </ButtonGroup>
    )

    expect(screen.getByText('Button 1')).toBeInTheDocument()
    expect(screen.getByText('Button 2')).toBeInTheDocument()
  })

  it('applies flex layout with gap', () => {
    const { container } = render(
      <ButtonGroup>
        <Button>Button 1</Button>
      </ButtonGroup>
    )

    expect(container.firstChild).toHaveClass('flex', 'gap-2')
  })

  it('merges custom className', () => {
    const { container } = render(
      <ButtonGroup className="custom-gap">
        <Button>Button</Button>
      </ButtonGroup>
    )

    expect(container.firstChild).toHaveClass('custom-gap')
  })
})

describe('Button Accessibility', () => {
  it('has proper ARIA attributes when loading', () => {
    render(<Button isLoading>Loading</Button>)
    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('disabled')
  })

  it('supports focus-visible outline', () => {
    const { container } = render(<Button>Focusable</Button>)
    const button = container.firstChild as HTMLElement
    expect(button).toHaveClass('focus-visible:outline-none', 'focus-visible:ring-2')
  })
})
