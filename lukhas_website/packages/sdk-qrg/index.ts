export type IssueReq = { purpose: "auth_stepup" | "wallet_tx"; ttl_ms?: number };
export type IssueRes = { glyphSvg: string; nonce: string; traceId: string };

const base = process.env.NEXT_PUBLIC_API_BASE || "";

export async function issue(req: IssueReq): Promise<IssueRes> {
  const r = await fetch(`${base}/qrg/issue`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    credentials: "include",
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error("qrg_issue_failed");
  return r.json();
}
