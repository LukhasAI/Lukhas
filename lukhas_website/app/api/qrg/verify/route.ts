import { NextRequest } from "next/server";
import { ok, badRequest } from "@/packages/api/respond";
import { prisma } from "@/lib/prisma";
import { verifyQrg } from "@/packages/qrg/jws";
import fs from "node:fs/promises";

export async function POST(req: NextRequest) {
  const { jws } = await req.json().catch(() => ({}));
  if (!jws) return badRequest("Missing jws");

  const pemPub = await fs.readFile(process.env.QRG_JWS_PUBLIC_KEY!, "utf8");
  const claims = verifyQrg(jws, pemPub);
  if (!claims) return ok({ ok: false });

  const sess = await prisma.qrgSession.findFirst({
    where: { userId: claims.sub, txId: claims.tx, status: "open", expiresAt: { gt: new Date() } }
  });
  if (!sess) return ok({ ok: false });

  // Optionally require WebAuthn step-up here
  await prisma.qrgSession.update({ where: { id: sess.id }, data: { status: "approved" } });
  return ok({ ok: true, txId: claims.tx, scope: claims.scope });
}
