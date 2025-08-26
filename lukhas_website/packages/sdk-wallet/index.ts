export type Balance = { currency: "LUK"; amount: number };
export type EarnInput = { reason: "nias_opt_in" | "contribution" | "affiliate"; amount?: number };
export type SpendInput = { reason: "mentor_mode"; amount: number };

const base = process.env.NEXT_PUBLIC_API_BASE || "";

export async function getBalance(): Promise<Balance> {
  const r = await fetch(`${base}/wallet/balance`, {
    cache: "no-store",
    credentials: "include"
  });
  if (!r.ok) throw new Error("balance_failed");
  return r.json();
}

export async function earn(input: EarnInput): Promise<Balance> {
  const r = await fetch(`${base}/wallet/earn`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    credentials: "include",
    body: JSON.stringify(input)
  });
  if (!r.ok) throw new Error("earn_failed");
  return r.json();
}

export async function spend(input: SpendInput): Promise<Balance> {
  const r = await fetch(`${base}/wallet/spend`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    credentials: "include",
    body: JSON.stringify(input)
  });
  if (!r.ok) throw new Error("spend_failed");
  return r.json();
}
