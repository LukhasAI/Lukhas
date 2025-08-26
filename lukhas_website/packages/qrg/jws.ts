import { createSign, createVerify, randomBytes } from "crypto";
import type { QrgClaims } from "./qrg-spec";

const ALG = "ES256";

const b64 = (o: any) => Buffer.from(JSON.stringify(o)).toString("base64url");

export function signQrg(claims: QrgClaims, pemPriv: string, kid: string) {
  const header = { alg: ALG, kid, typ: "JWT" };
  const head = b64(header);
  const payload = b64(claims);
  const toSign = `${head}.${payload}`;
  const sign = createSign("SHA256");
  sign.update(toSign);
  sign.end();
  const sig = sign.sign(pemPriv).toString("base64url");
  return `${toSign}.${sig}`;
}

export function verifyQrg(jws: string, pemPub: string): QrgClaims | null {
  const [head, payload, sig] = jws.split(".");
  if (!head || !payload || !sig) return null;
  const verify = createVerify("SHA256");
  verify.update(`${head}.${payload}`);
  verify.end();
  const ok = verify.verify(pemPub, Buffer.from(sig, "base64url"));
  return ok ? JSON.parse(Buffer.from(payload, "base64url").toString()) : null;
}

export function newNonce() {
  return randomBytes(32).toString("base64url");
}
