"use client";
import React, { useState } from "react";

type PublicKeyCredentialJSON = {
  id: string;
  rawId: string;
  type: PublicKeyCredential["type"];
  authenticatorAttachment?: PublicKeyCredential["authenticatorAttachment"];
  clientExtensionResults: Record<string, unknown>;
  response: {
    clientDataJSON: string;
    authenticatorData?: string;
    signature?: string;
    userHandle?: string;
  };
};

type SecureOpenContext = {
  stepUpToken: string;
  rawChallenge: string;
  credential: PublicKeyCredentialJSON;
};

type StepUpStartResponse = {
  success: boolean;
  challenge: string;
  allowCredentials?: Array<{
    id: string;
    type: PublicKeyCredentialType;
    transports?: AuthenticatorTransport[];
  }>;
  rpId?: string;
  userVerification?: UserVerificationRequirement;
  timeout?: number;
};

type StepUpFinishResponse = {
  success: boolean;
  stepUpToken?: string;
  error?: string;
};

export type QRGEnvelopeProps = {
  filename: string;
  sizeMB: number;
  level: "confidential"|"secret";
  onOpen?: (context: SecureOpenContext) => Promise<Blob|ArrayBuffer|string>;
};

function base64UrlToArrayBuffer(value: string): ArrayBuffer {
  const normalized = value
    .replace(/-/g, "+")
    .replace(/_/g, "/")
    .padEnd(value.length + ((4 - (value.length % 4 || 4)) % 4), "=");

  const binary = atob(normalized);
  const bytes = new Uint8Array(binary.length);

  for(let i=0;i<binary.length;i++){
    bytes[i] = binary.charCodeAt(i);
  }

  return bytes.buffer;
}

function arrayBufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";

  for(let i=0;i<bytes.byteLength;i++){
    binary += String.fromCharCode(bytes[i]);
  }

  const base64 = btoa(binary);
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function publicKeyCredentialToJSON(credential: PublicKeyCredential): PublicKeyCredentialJSON {
  const response = credential.response as AuthenticatorAssertionResponse;

  return {
    id: credential.id,
    rawId: arrayBufferToBase64Url(credential.rawId),
    type: credential.type,
    authenticatorAttachment: credential.authenticatorAttachment ?? undefined,
    clientExtensionResults:
      typeof credential.getClientExtensionResults === "function"
        ? credential.getClientExtensionResults()
        : {},
    response: {
      clientDataJSON: arrayBufferToBase64Url(response.clientDataJSON),
      authenticatorData: response.authenticatorData
        ? arrayBufferToBase64Url(response.authenticatorData)
        : undefined,
      signature: response.signature ? arrayBufferToBase64Url(response.signature) : undefined,
      userHandle: response.userHandle ? arrayBufferToBase64Url(response.userHandle) : undefined
    }
  };
}

export default function QRGEnvelope({ filename, sizeMB, level, onOpen }: QRGEnvelopeProps){
  const [open,setOpen] = useState(false);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState<string|null>(null);

  async function handleOpen() {
    if(!onOpen) return;

    if(typeof window === "undefined" || !window.PublicKeyCredential || !navigator.credentials?.get){
      setError("Secure device authentication is not available in this environment");
      return;
    }

    setBusy(true);
    setError(null);

    try {
      const startResponse = await fetch("/api/auth/stepup/start", { method: "POST" });

      if(!startResponse.ok){
        const payload = (await startResponse.json().catch(()=>({}))) as { error?: string };
        throw new Error(payload?.error || "Unable to initiate secure challenge");
      }

      const startData = (await startResponse.json()) as StepUpStartResponse;

      if(!startData?.success || !startData.challenge){
        throw new Error("Authentication challenge was not provided by the server");
      }

      const publicKey: PublicKeyCredentialRequestOptions = {
        challenge: base64UrlToArrayBuffer(startData.challenge),
        userVerification: startData.userVerification ?? "required",
        timeout: startData.timeout ?? 60_000,
        rpId: startData.rpId
      };

      if(startData.allowCredentials?.length){
        publicKey.allowCredentials = startData.allowCredentials.map(item => ({
          ...item,
          id: base64UrlToArrayBuffer(item.id)
        }));
      }

      const assertion = await navigator.credentials.get({ publicKey });

      if(!assertion){
        throw new Error("Authentication was cancelled");
      }

      const finishResponse = await fetch("/api/auth/stepup/finish", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(publicKeyCredentialToJSON(assertion))
      });

      const finishData = (await finishResponse.json().catch(()=>({}))) as StepUpFinishResponse;

      if(!finishResponse.ok || !finishData.success || !finishData.stepUpToken){
        throw new Error(finishData?.error || "Device verification failed");
      }

      const context: SecureOpenContext = {
        stepUpToken: finishData.stepUpToken,
        rawChallenge: startData.challenge,
        credential: publicKeyCredentialToJSON(assertion)
      };

      const result = await onOpen(context);
      console.log("QRG envelope opened:", result);

      setOpen(true);
    } catch (err) {
      setError("Authentication failed or content unavailable");
      console.error("QRG envelope error:", err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <button
      onClick={handleOpen}
      disabled={busy}
      title={`${filename} · ${sizeMB}MB · ${level}`}
      style={{
        display:"grid",
        gap:8,
        padding:12,
        border:`1px solid ${level==="secret" ? "#a78bfa" : "#3b82f6"}`,
        borderRadius:12,
        background: open
          ? "rgba(167,139,250,.15)"
          : busy
          ? "rgba(59,130,246,.1)"
          : "transparent",
        color:"var(--text)",
        cursor: busy ? "wait" : "pointer",
        opacity: busy ? 0.7 : 1,
        transition: "all 0.2s ease",
        textAlign: "left" as const
      }}
    >
      <div style={{display:"flex", alignItems:"center", gap:10}}>
        <div style={{
          width:12,
          height:12,
          borderRadius:999,
          background: level==="secret" ? "#a78bfa" : "#3b82f6",
          flexShrink: 0,
          position: "relative" as const
        }}>
          {busy && (
            <div style={{
              position: "absolute" as const,
              inset: -2,
              border: "2px solid transparent",
              borderTop: `2px solid ${level==="secret" ? "#a78bfa" : "#3b82f6"}`,
              borderRadius: "50%",
              animation: "spin 1s linear infinite"
            }} />
          )}
        </div>
        <strong style={{fontSize:14, fontWeight:600}}>
          {busy ? "Authenticating..." : open ? "Glyph Opened" : "Glyph Envelope"}
        </strong>
        <div style={{marginLeft:"auto", fontSize:11, opacity:.7}}>
          {level.toUpperCase()}
        </div>
      </div>

      <div style={{fontSize:13, opacity:.9, fontWeight:500}}>
        {filename} · {sizeMB}MB
      </div>

      <div style={{fontSize:12, opacity:.7, fontStyle:"italic"}}>
        {error ? (
          <span style={{color:"#ef4444"}}>⚠️ {error}</span>
        ) : busy ? (
          "Verifying identity & decrypting content..."
        ) : open ? (
          "✓ Content decrypted and accessible"
        ) : (
          "🔒 Click to authenticate & decrypt"
        )}
      </div>

      {open && (
        <div style={{
          marginTop: 4,
          padding: 8,
          background: "rgba(59,130,246,.1)",
          borderRadius: 8,
          fontSize: 12,
          opacity: 0.9
        }}>
          <strong>Security Note:</strong> Content has been decrypted using your device key.
          This session is logged to the Λ-trace for audit purposes.
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </button>
  );
}
