import { render, screen } from '@testing-library/react';
import { TransparencyBox } from '@/components/TransparencyBox';

describe('TransparencyBox', () => {
  test('renders all required sections', () => {
    render(
      <TransparencyBox
        capabilities={['Can do A', 'Can do B']}
        limitations={['Cannot do X', 'Cannot do Y']}
        dependencies={['Needs service C', 'Needs API D']}
        dataHandling={['Stores data E', 'Processes data F']}
      />
    );

    // Check all section headers are present
    expect(screen.getByRole('heading', { name: /Capabilities/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Limitations/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Dependencies/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Data handling/i })).toBeInTheDocument();

    // Check content is rendered
    expect(screen.getByText('Can do A')).toBeInTheDocument();
    expect(screen.getByText('Cannot do X')).toBeInTheDocument();
    expect(screen.getByText('Needs service C')).toBeInTheDocument();
    expect(screen.getByText('Stores data E')).toBeInTheDocument();
  });

  test('renders Spanish headers when locale is es', () => {
    render(
      <TransparencyBox
        locale="es"
        capabilities={['Puede hacer A']}
        limitations={['No puede hacer X']}
        dependencies={['Necesita servicio C']}
        dataHandling={['Almacena datos E']}
      />
    );

    expect(screen.getByRole('heading', { name: /Capacidades/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Limitaciones/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Dependencias/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Tratamiento de datos/i })).toBeInTheDocument();
  });

  test('has correct data attributes for testing', () => {
    const { container } = render(
      <TransparencyBox
        capabilities={['A']}
        limitations={['B']}
        dependencies={['C']}
        dataHandling={['D']}
      />
    );

    expect(container.querySelector('[data-transparency="present"]')).toBeInTheDocument();
    expect(container.querySelector('[data-section="capabilities"]')).toBeInTheDocument();
    expect(container.querySelector('[data-section="limitations"]')).toBeInTheDocument();
    expect(container.querySelector('[data-section="dependencies"]')).toBeInTheDocument();
    expect(container.querySelector('[data-section="dataHandling"]')).toBeInTheDocument();
  });

  test('has proper ARIA attributes', () => {
    render(
      <TransparencyBox
        title="Custom Title"
        capabilities={['A']}
        limitations={['B']}
        dependencies={['C']}
        dataHandling={['D']}
      />
    );

    const region = screen.getByRole('region', { name: /Custom Title/i });
    expect(region).toBeInTheDocument();
    expect(region).toHaveAttribute('aria-label', 'Custom Title');
  });

  test('warns in development when sections are missing', () => {
    const originalEnv = process.env.NODE_ENV;
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

    // Set to development
    process.env.NODE_ENV = 'development';

    render(
      <TransparencyBox
        capabilities={[]}
        limitations={['B']}
        dependencies={['C']}
        dataHandling={['D']}
      />
    );

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('Missing sections: capabilities')
    );

    // Restore
    process.env.NODE_ENV = originalEnv;
    consoleSpy.mockRestore();
  });
});
