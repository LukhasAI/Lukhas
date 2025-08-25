"use client";
import { startSignIn } from "@/packages/sdk-identity";

export default function AuthPage() {
  const enabled = process.env.NEXT_PUBLIC_AUTH_ENABLED !== "false";

  async function onSignIn() {
    try {
      const res = await startSignIn({});
      // Next: call WebAuthn get()/passkey with res.challengeId; fall back to magic link.
      alert(`Sign-in challenge: ${res.challengeId}`);
    } catch {
      alert("Sign-in not available.");
    }
  }

  if (!enabled) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-white/60">Auth disabled by flag.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-light mb-2 lukhas-brand">LUKHΛS</h1>
            <p className="text-white/60">Sign in to your account</p>
          </div>
          
          <div className="space-y-4">
            <button 
              onClick={onSignIn}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors"
            >
              Continue with Passkey
            </button>
            
            <p className="text-center text-sm text-white/60">
              Having trouble? Use email link or step-up via QRG.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}