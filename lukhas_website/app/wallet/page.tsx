"use client";
import { useEffect, useState } from "react";
import { getBalance, earn, spend } from "@/packages/sdk-wallet";

export default function WalletPage() {
  const enabled = process.env.NEXT_PUBLIC_WALLET_ENABLED !== "false";
  const niasEnabled = process.env.NEXT_PUBLIC_NIAS_ENABLED !== "false";
  const [bal, setBal] = useState<{ currency: "LUK"; amount: number } | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function refresh() {
    try { 
      setBal(await getBalance()); 
      setMsg(null);
    } catch { 
      setMsg("Balance unavailable (API down?)"); 
    }
  }
  
  useEffect(() => { 
    if (enabled) refresh(); 
  }, [enabled]);

  async function onEarn() {
    setBusy(true);
    try { 
      const b = await earn({ reason: "nias_opt_in", amount: 10 }); 
      setBal(b); 
      setMsg("✅ Earned 10 LUK via NIAS opt-in."); 
    } catch { 
      setMsg("❌ Earn failed."); 
    } finally { 
      setBusy(false); 
    }
  }
  
  async function onSpend() {
    setBusy(true);
    try { 
      const b = await spend({ reason: "mentor_mode", amount: 10 }); 
      setBal(b); 
      setMsg("✅ Spent 10 LUK for Mentor Mode."); 
    } catch { 
      setMsg("❌ Spend failed."); 
    } finally { 
      setBusy(false); 
    }
  }

  if (!enabled) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-white/60">Wallet disabled by flag.</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-light mb-2">WΛLLET</h1>
            <p className="text-white/60">Your LUKHAS token balance and transactions</p>
          </div>

          {/* Balance Display */}
          <div className="bg-white/5 rounded-lg p-8 border border-white/10 mb-8 text-center">
            <div className="text-6xl font-light mb-2">
              {bal ? `${bal.amount}` : "—"}
            </div>
            <div className="text-xl text-white/60">
              {bal ? `${bal.currency}` : "Loading..."}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {niasEnabled && (
              <button 
                onClick={onEarn} 
                disabled={busy}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white py-3 px-4 rounded-lg transition-colors"
              >
                {busy ? "Processing..." : "Earn 10 LUK (NIAS)"}
              </button>
            )}
            
            <button 
              onClick={onSpend} 
              disabled={busy || !bal || bal.amount < 10}
              className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:opacity-50 text-white py-3 px-4 rounded-lg transition-colors"
            >
              {busy ? "Processing..." : "Spend 10 LUK (Mentor Mode)"}
            </button>
            
            <button 
              onClick={refresh} 
              disabled={busy}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white py-3 px-4 rounded-lg transition-colors"
            >
              {busy ? "Loading..." : "Refresh"}
            </button>
          </div>

          {/* Status Message */}
          {msg && (
            <div className="bg-white/5 rounded-lg p-4 border border-white/10 text-center">
              <p className="text-white/80">{msg}</p>
            </div>
          )}

          {/* Demo Information */}
          <div className="mt-8 p-4 bg-white/5 rounded-lg border border-white/10">
            <h3 className="font-medium mb-2">Demo Flow:</h3>
            <ul className="text-sm text-white/60 space-y-1">
              <li>• <strong>Earn:</strong> Opt into NIAS to receive 10 LUK tokens</li>
              <li>• <strong>Spend:</strong> Use 10 LUK to unlock Mentor Mode in Studio</li>
              <li>• <strong>Refresh:</strong> Update your balance from the API</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  );
}