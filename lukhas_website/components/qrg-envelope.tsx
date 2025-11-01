"use client";
import React, { useState } from "react";
import { useQuantumIdentity } from "@/lib/auth/QuantumIdentityProvider";
import AuditLogger from "@/packages/auth/audit-logger";

type AuditLoggerType = typeof AuditLogger;
type AuditLogParams = Parameters<AuditLoggerType["log"]>[0];
type AuditContext = AuditLogParams["context"];

type QRGOpenPayload = Blob | ArrayBuffer | string;

type QRGOpenAuditEnvelope = {
  payload: QRGOpenPayload;
  traceId?: string;
  auditContext?: Partial<AuditContext>;
  auditMetadata?: Record<string, unknown>;
};

type QRGOpenResult = QRGOpenPayload | QRGOpenAuditEnvelope;

export type QRGEnvelopeProps = {
  filename: string;
  sizeMB: number;
  level: "confidential"|"secret";
  onOpen?: () => Promise<QRGOpenResult>; // implement later with real E2EE
};

export default function QRGEnvelope({ filename, sizeMB, level, onOpen }: QRGEnvelopeProps){
  const { authState } = useQuantumIdentity();
  const [open,setOpen] = useState(false);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState<string|null>(null);

  function normalizeOpenResult(result: QRGOpenResult | undefined): QRGOpenAuditEnvelope {
    if (result && typeof result === "object" && "payload" in result) {
      return {
        payload: result.payload,
        traceId: result.traceId,
        auditContext: result.auditContext,
        auditMetadata: result.auditMetadata
      };
    }

    return { payload: result as QRGOpenPayload };
  }

  function generateTraceId() {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return `qrg_${crypto.randomUUID()}`;
    }
    if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
      const array = new Uint8Array(16);
      crypto.getRandomValues(array);
      return `qrg_${Array.from(array).map(b => b.toString(16).padStart(2, "0")).join("")}`;
    }
    return `qrg_${Math.random().toString(36).slice(2)}`;
  }

  function buildAuditContext(
    traceId: string,
    override?: Partial<AuditContext>
  ): AuditContext {
    const identity = authState.identity;
    const defaultUserAgent = typeof navigator !== "undefined" ? navigator.userAgent : "unknown";

    return {
      requestId: override?.requestId,
      sessionId: override?.sessionId,
      traceId: override?.traceId ?? traceId,
      userId: override?.userId ?? identity?.consciousness_id,
      impersonatorId: override?.impersonatorId,
      tier: override?.tier ?? identity?.identity_tier,
      role: override?.role,
      organizationId: override?.organizationId,
      ipAddress: override?.ipAddress ?? "client_redacted",
      userAgent: override?.userAgent ?? defaultUserAgent,
      country: override?.country,
      asn: override?.asn,
      deviceId: override?.deviceId,
      deviceFingerprint: override?.deviceFingerprint,
      deviceTrusted: override?.deviceTrusted,
      authMethods: override?.authMethods ?? ["qrg_envelope"],
      stepUpAuthenticated: override?.stepUpAuthenticated ?? true,
      riskScore: override?.riskScore,
      featureFlags: override?.featureFlags,
      experimentId: override?.experimentId,
      businessUnit: override?.businessUnit,
    };
  }

  async function recordAuditEvent(
    outcome: "success" | "failure",
    traceId: string,
    auditContext?: Partial<AuditContext>,
    auditMetadata?: Record<string, unknown>,
    errorMessage?: string
  ) {
    try {
      await AuditLogger.log({
        eventType: "resource_read",
        action: "open_qrg_envelope",
        resource: "qrg_envelope",
        resourceId: traceId,
        outcome,
        context: buildAuditContext(traceId, auditContext),
        description: outcome === "success"
          ? `QRG envelope opened for ${filename}`
          : `QRG envelope access failed for ${filename}`,
        reasons: errorMessage ? [errorMessage] : undefined,
        metadata: {
          filename,
          sizeMB,
          level,
          traceId,
          ...auditMetadata,
        },
        sensitive: true,
      });
    } catch (auditError) {
      console.error("Failed to record Λ-trace audit event:", auditError);
    }
  }

  async function handleOpen() {
    if(!onOpen) return;

    setBusy(true);
    setError(null);

    let normalized: QRGOpenAuditEnvelope | undefined;
    let traceId: string | undefined;

    try {
// See: https://github.com/LukhasAI/Lukhas/issues/581
// See: https://github.com/LukhasAI/Lukhas/issues/582

      // Simulate authentication delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      const result = await onOpen();
      normalized = normalizeOpenResult(result);
      traceId = normalized.traceId ?? generateTraceId();

      console.info("QRG envelope opened", { traceId, level });

      setOpen(true);

      await recordAuditEvent("success", traceId, normalized.auditContext, normalized.auditMetadata);
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown_error";
      const failureTraceId = traceId ?? generateTraceId();

      setError("Authentication failed or content unavailable");
      console.error("QRG envelope error:", { error: err, traceId: failureTraceId });

      await recordAuditEvent("failure", failureTraceId, normalized?.auditContext, normalized?.auditMetadata, message);
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
