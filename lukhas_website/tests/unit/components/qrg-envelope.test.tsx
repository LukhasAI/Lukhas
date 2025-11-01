require('ts-node/register/transpile-only');

const React = require('react');
const { act, render, screen, waitFor } = require('@testing-library/react');
const userEvent = require('@testing-library/user-event').default;
const QRGEnvelope = require('../../../components/qrg-envelope').default;

const mockAuditLog = jest.fn();

jest.mock('../../../packages/auth/audit-logger', () => ({
  __esModule: true,
  default: { log: mockAuditLog },
  AuditLogger: { log: mockAuditLog },
}));

jest.mock('../../../lib/auth/QuantumIdentityProvider', () => ({
  __esModule: true,
  useQuantumIdentity: () => ({
    authState: {
      isAuthenticated: true,
      identity: {
        consciousness_id: 'LUKHAS_TEST_ID',
        quantum_signature: 'QS_TEST',
        domain_access: ['lukhas.ai'],
        coherence_score: 0.97,
        identity_tier: 'T3',
        created_at: new Date().toISOString(),
        last_transition: new Date().toISOString(),
        cross_domain_state: new Map(),
      },
    },
  }),
}));

describe('QRGEnvelope', () => {
  beforeEach(() => {
    mockAuditLog.mockReset();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('records Λ-trace audit metadata on successful open', async () => {
    mockAuditLog.mockResolvedValue('audit_success');
    const onOpen = jest.fn().mockResolvedValue({
      payload: 'secret-message',
      traceId: 'trace-123',
      auditContext: {
        ipAddress: '10.0.0.1',
        userAgent: 'jest-test-agent',
        sessionId: 'session-123',
      },
      auditMetadata: { channel: 'p2p' },
    });

    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

    render(
      React.createElement(QRGEnvelope, {
        filename: 'secret.txt',
        sizeMB: 1.5,
        level: 'confidential',
        onOpen,
      })
    );

    const button = screen.getByRole('button', { name: /Glyph Envelope/i });

    await user.click(button);
    await act(async () => {
      jest.advanceTimersByTime(1500);
    });

    await waitFor(() => expect(onOpen).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(mockAuditLog).toHaveBeenCalledTimes(1));

    const callArgs = mockAuditLog.mock.calls[0][0];

    expect(callArgs.outcome).toBe('success');
    expect(callArgs.context.traceId).toBe('trace-123');
    expect(callArgs.context.userId).toBe('LUKHAS_TEST_ID');
    expect(callArgs.metadata).toMatchObject({
      filename: 'secret.txt',
      sizeMB: 1.5,
      level: 'confidential',
      traceId: 'trace-123',
      channel: 'p2p',
    });
    expect(callArgs.reasons).toBeUndefined();
  });

  it('records failure Λ-trace entry when open fails', async () => {
    mockAuditLog.mockResolvedValue('audit_failure');
    const onOpen = jest.fn().mockRejectedValue(new Error('decryption_failed'));

    const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

    render(
      React.createElement(QRGEnvelope, {
        filename: 'secret.txt',
        sizeMB: 2.3,
        level: 'secret',
        onOpen,
      })
    );

    const button = screen.getByRole('button', { name: /Glyph Envelope/i });

    await user.click(button);
    await act(async () => {
      jest.advanceTimersByTime(1500);
    });

    await waitFor(() => expect(onOpen).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(mockAuditLog).toHaveBeenCalledTimes(1));

    const callArgs = mockAuditLog.mock.calls[0][0];

    expect(callArgs.outcome).toBe('failure');
    expect(callArgs.metadata).toMatchObject({
      filename: 'secret.txt',
      level: 'secret',
    });
    expect(callArgs.reasons?.[0]).toContain('decryption_failed');
    expect(callArgs.context.traceId).toMatch(/^qrg_/);
    expect(await screen.findByText(/Authentication failed or content unavailable/i)).toBeInTheDocument();
  });
});
