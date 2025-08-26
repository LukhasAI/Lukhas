import { NextRequest, NextResponse } from "next/server";
import crypto from "node:crypto";
import { prisma } from "@/lib/prisma";
import { generatePkPass } from "@/packages/wallet/apple-pass";

export async function GET(_req: NextRequest) {
  const userId = ""; // TODO resolve from session
  const user = await prisma.user.findUnique({ where: { id: userId }, include: { aliases: true }});
  if (!user) return NextResponse.json({ ok: false }, { status: 401 });

  const alias = user.aliases?.[0]?.aliasDisplay ?? "ΛiD#GLO/GLO/H-XXXX-XXXX-X";
  const serialNumber = crypto.randomUUID();
  const oneTimeCode = String(Math.floor(100000 + Math.random() * 900000));
  const expires = Math.floor(Date.now() / 1000) + (parseInt(process.env.WALLET_CODE_TTL_SECONDS || "60", 10));

  await prisma.walletPass.create({
    data: { id: crypto.randomUUID(), userId, platform: "apple", serialNumber, lastRotatedAt: new Date() }
  });

  try {
    const buf = await generatePkPass({
      serialNumber, userId, alias, oneTimeCode, action: "wallet.bind", txId: serialNumber, expires
    });

    const res = new NextResponse(buf, { status: 200 });
    res.headers.set("Content-Type", "application/vnd.apple.pkpass");
    res.headers.set("Content-Disposition", `attachment; filename="lukhas-id.pkpass"`);
    return res;
  } catch (error) {
    // If passkit-generator not installed, return error
    console.error("PKPass generation failed:", error);
    return NextResponse.json({
      error: "PKPass generation not available. Install passkit-generator package."
    }, { status: 501 });
  }
}
