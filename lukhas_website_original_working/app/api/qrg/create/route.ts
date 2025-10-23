import { NextRequest } from "next/server";
import { ok, badRequest } from "@/packages/api/respond";
import { prisma } from "@/lib/prisma";
import { signQrg, newNonce } from "@/packages/qrg/jws";
import fs from "node:fs/promises";
import crypto from "node:crypto";

export async function POST(req: NextRequest) {
  const { scope, txId } = await req.json().catch(() => ({}));
  if (!scope || !txId) return badRequest("Missing scope/txId");

  const userId = ""; // TODO resolve from session
  const ttl = parseInt(process.env.QRG_TTL_SECONDS || "60", 10);
  const now = Math.floor(Date.now() / 1000);
  const exp = now + ttl;

  const pemPriv = await fs.readFile(process.env.QRG_JWS_PRIVATE_KEY!, "utf8");
  const kid = process.env.QRG_JWS_KID!;
  const jws = signQrg(
    { v: "qrg/v1", iss: "lukhas", aud: "lid", sub: userId, tx: txId, scope, nonce: newNonce(), iat: now, exp },
    pemPriv,
    kid
  );

  const id = crypto.randomUUID();
  await prisma.qrgSession.create({
    data: {
      id, userId, nonce: "", txId, scope, status: "open",
      issuedAt: new Date(), expiresAt: new Date(Date.now() + ttl * 1000), jws
    }
  });

  const uri = `qrg://v1/approve?jws=${encodeURIComponent(jws)}`;
  return ok({ id, ttl, uri });
}