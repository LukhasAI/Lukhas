export type ConsentRecord = { userId: string; scope: string; granted: boolean; timestamp: string };
export type ConsentInput = { scope: string; granted: boolean };

const base = process.env.NEXT_PUBLIC_API_BASE || "";

export async function recordConsent(input: ConsentInput): Promise<ConsentRecord> {
  const r = await fetch(`${base}/consent/record`, {
    method: "POST", 
    headers: { "content-type": "application/json" }, 
    credentials: "include",
    body: JSON.stringify(input)
  });
  if (!r.ok) throw new Error("consent_record_failed");
  return r.json();
}

export async function getConsents(): Promise<ConsentRecord[]> {
  const r = await fetch(`${base}/consent/records`, { 
    credentials: "include" 
  });
  if (!r.ok) throw new Error("consent_get_failed");
  return r.json();
}