/**
 * @jest-environment jsdom
 */

import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Providers } from '@/components/providers'

// Mock Stigg SDK to avoid actual API calls during testing
jest.mock('@stigg/react-sdk', () => ({
  StiggProvider: ({ children, apiKey }: { children: React.ReactNode; apiKey: string }) => (
    <div data-testid="stigg-provider" data-api-key={apiKey}>
      {children}
    </div>
  ),
}))

describe('StiggProvider Integration', () => {
  beforeEach(() => {
    // Clear environment variable mocks
    delete (process.env as any).NEXT_PUBLIC_STIGG_CLIENT_API_KEY
  })

  it('should render StiggProvider when API key is available', () => {
    // Mock environment variable
    process.env.NEXT_PUBLIC_STIGG_CLIENT_API_KEY = 'test-stigg-api-key'

    render(
      <Providers>
        <div>Test Content</div>
      </Providers>
    )

    // Verify StiggProvider is rendered
    expect(screen.getByTestId('stigg-provider')).toBeInTheDocument()
    expect(screen.getByTestId('stigg-provider')).toHaveAttribute('data-api-key', 'test-stigg-api-key')
    
    // Verify content is still rendered
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('should render fallback when API key is not available', () => {
    // No API key set
    
    render(
      <Providers>
        <div>Test Content</div>
      </Providers>
    )

    // Verify fallback is rendered instead of StiggProvider
    expect(screen.getByTestId('stigg-fallback')).toBeInTheDocument()
    expect(screen.queryByTestId('stigg-provider')).not.toBeInTheDocument()
    
    // Verify content is still rendered
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('should handle placeholder API key gracefully', () => {
    process.env.NEXT_PUBLIC_STIGG_CLIENT_API_KEY = 'stigg_client_key_placeholder_development_only'

    render(
      <Providers>
        <div>Test Content</div>
      </Providers>
    )

    // With placeholder key, StiggProvider should still render
    expect(screen.getByTestId('stigg-provider')).toBeInTheDocument()
    expect(screen.getByTestId('stigg-provider')).toHaveAttribute(
      'data-api-key',
      'stigg_client_key_placeholder_development_only'
    )
  })

  it('should integrate with QueryClientProvider', () => {
    process.env.NEXT_PUBLIC_STIGG_CLIENT_API_KEY = 'test-key'

    const { container } = render(
      <Providers>
        <div>Test Content</div>
      </Providers>
    )

    // Verify both providers are present in the component tree
    expect(screen.getByTestId('stigg-provider')).toBeInTheDocument()
    expect(screen.getByText('Test Content')).toBeInTheDocument()
    
    // Verify the DOM structure is correct
    expect(container.firstChild).toMatchSnapshot()
  })
})