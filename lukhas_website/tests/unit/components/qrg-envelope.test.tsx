import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import QRGEnvelope from "@/components/qrg-envelope";

describe("QRGEnvelope", () => {
  const originalFetch = global.fetch;
  const originalCredentials = navigator.credentials;
  const originalPublicKeyCredential = window.PublicKeyCredential;

  const mockCredential = {
    id: "cred-123",
    type: "public-key" as const,
    rawId: new Uint8Array([1, 2, 3]).buffer,
    response: {
      clientDataJSON: new TextEncoder().encode("client").buffer,
      authenticatorData: new Uint8Array([4, 5, 6]).buffer,
      signature: new Uint8Array([7, 8]).buffer,
      userHandle: new Uint8Array([9]).buffer,
    },
    authenticatorAttachment: "platform" as const,
    getClientExtensionResults: jest.fn(() => ({ appid: true })),
  } as unknown as PublicKeyCredential;

  beforeEach(() => {
    global.fetch = jest.fn();
    Object.defineProperty(navigator, "credentials", {
      configurable: true,
      value: { get: jest.fn().mockResolvedValue(mockCredential) },
    });
    Object.defineProperty(window, "PublicKeyCredential", {
      configurable: true,
      value: function PublicKeyCredential() {} as unknown,
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
    if (originalFetch) {
      global.fetch = originalFetch;
    }
    Object.defineProperty(navigator, "credentials", {
      configurable: true,
      value: originalCredentials,
    });
    Object.defineProperty(window, "PublicKeyCredential", {
      configurable: true,
      value: originalPublicKeyCredential,
    });
  });

  it("performs a WebAuthn challenge before opening", async () => {
    const mockStart = {
      success: true,
      challenge: "ZmFrZS1jaGFsbGVuZ2U", // base64url for "fake-challenge"
    };
    const mockFinish = {
      success: true,
      stepUpToken: "token-abc",
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValue(mockStart),
    });

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValue(mockFinish),
    });

    const onOpen = jest.fn().mockResolvedValue("decrypted");

    render(
      <QRGEnvelope
        filename="secret.txt"
        sizeMB={4.2}
        level="secret"
        onOpen={onOpen}
      />
    );

    fireEvent.click(screen.getByRole("button"));

    await waitFor(() => expect(onOpen).toHaveBeenCalledTimes(1));

    expect(onOpen).toHaveBeenCalledWith(
      expect.objectContaining({
        stepUpToken: "token-abc",
        rawChallenge: "ZmFrZS1jaGFsbGVuZ2U",
      })
    );

    await screen.findByText("Glyph Opened");

    expect((navigator.credentials as any).get).toHaveBeenCalledWith(
      expect.objectContaining({
        publicKey: expect.objectContaining({
          userVerification: "required",
          rpId: undefined,
        }),
      })
    );
  });

  it("shows an error message when the challenge fails to start", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: jest.fn().mockResolvedValue({ error: "No session" }),
    });

    const onOpen = jest.fn();

    render(
      <QRGEnvelope
        filename="secret.txt"
        sizeMB={2}
        level="confidential"
        onOpen={onOpen}
      />
    );

    fireEvent.click(screen.getByRole("button"));

    await screen.findByText("⚠️ Authentication failed or content unavailable");
    expect(onOpen).not.toHaveBeenCalled();
  });
});
