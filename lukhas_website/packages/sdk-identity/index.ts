export type SignInStart = { username?: string };
export type SignInResult = { challengeId: string };

const base = process.env.NEXT_PUBLIC_API_BASE || "";

export async function startSignIn(payload: SignInStart): Promise<SignInResult> {
  const r = await fetch(`${base}/identity/signin/start`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!r.ok) throw new Error("signin_start_failed");
  return r.json();
}
