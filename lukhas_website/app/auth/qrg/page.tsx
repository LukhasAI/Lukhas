"use client";
import { useEffect, useState } from "react";
import { issue } from "@/packages/sdk-qrg";

export default function QRGStepUp() {
  const [svg, setSvg] = useState<string | null>(null);
  const [trace, setTrace] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const enabled = process.env.NEXT_PUBLIC_QRG_ENABLED !== "false";

  useEffect(() => {
    if (!enabled) return;
    
    setLoading(true);
    issue({ purpose: "auth_stepup", ttl_ms: 20000 })
      .then(({ glyphSvg, traceId }) => { 
        setSvg(glyphSvg); 
        setTrace(traceId); 
      })
      .catch(() => {
        setSvg(null);
        setTrace(null);
      })
      .finally(() => setLoading(false));
  }, [enabled]);

  if (!enabled) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-white/60">QRG disabled.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-lg text-center">
          <h1 className="text-3xl font-light mb-2 lukhas-brand">Scan to Verify</h1>
          <p className="text-white/60 mb-8">Use your device to scan the QRG below</p>
          
          <div className="bg-white/5 rounded-lg p-8 border border-white/10">
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
                <p className="text-white/40">Failed to load QRG</p>
              </div>
            )}
          </div>
          
          {trace && (
            <p className="text-xs text-white/40 mt-4">
              Trace: {trace}
            </p>
          )}
          
          <div className="mt-6">
            <a 
              href="/auth" 
              className="text-blue-400 hover:text-blue-300 text-sm underline"
            >
              ← Back to sign in
            </a>
          </div>
        </div>
      </div>
    </main>
  );
}