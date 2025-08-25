"use client";
import { useState } from "react";
import { issue } from "@/packages/sdk-qrg";

export default function QRGDemo() {
  const [svg, setSvg] = useState<string | null>(null);
  const [trace, setTrace] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const enabled = process.env.NEXT_PUBLIC_QRG_ENABLED !== "false";

  async function onIssue() {
    setLoading(true);
    try {
      const { glyphSvg, traceId } = await issue({ purpose: "wallet_tx", ttl_ms: 15000 });
      setSvg(glyphSvg); 
      setTrace(traceId);
    } catch {
      setSvg(null);
      setTrace(null);
    } finally {
      setLoading(false);
    }
  }

  if (!enabled) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-white/60">QRG disabled by flag.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-2xl text-center">
          <div className="mb-8">
            <h1 className="text-4xl font-light mb-2">QRG Demo</h1>
            <p className="text-white/60">Generate Quantum Resistant Glyphs for wallet transactions</p>
          </div>

          <div className="mb-8">
            <button 
              onClick={onIssue}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white py-3 px-6 rounded-lg transition-colors"
            >
              {loading ? "Generating..." : "Issue QRG"}
            </button>
          </div>

          {/* QRG Display */}
          <div className="bg-white/5 rounded-lg p-8 border border-white/10 mb-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              </div>
            ) : svg ? (
              <div 
                className="flex items-center justify-center"
                dangerouslySetInnerHTML={{ __html: svg }} 
              />
            ) : (
              <div className="flex items-center justify-center h-64">
                <p className="text-white/40">Click "Issue QRG" to generate a glyph</p>
              </div>
            )}
          </div>

          {trace && (
            <div className="bg-white/5 rounded-lg p-4 border border-white/10 mb-6">
              <h3 className="text-sm font-medium mb-2">Trace Information</h3>
              <p className="text-xs text-white/60 font-mono break-all">{trace}</p>
            </div>
          )}

          {/* Information */}
          <div className="text-left bg-white/5 rounded-lg p-6 border border-white/10">
            <h3 className="font-medium mb-3">About QRG</h3>
            <ul className="text-sm text-white/60 space-y-2">
              <li>• <strong>Purpose:</strong> Secure wallet transaction verification</li>
              <li>• <strong>TTL:</strong> 15 seconds (15,000ms) for security</li>
              <li>• <strong>Quantum Resistant:</strong> Uses post-quantum cryptography</li>
              <li>• <strong>Traceable:</strong> Each glyph has a unique trace ID</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  );
}