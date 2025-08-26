import path from "node:path";
import fs from "node:fs/promises";

// Note: This requires 'passkit-generator' package
// npm i passkit-generator
// If not installed, functions will throw

export type PassFields = {
  serialNumber: string;
  userId: string;
  alias: string;        // ΛiD#... (display only)
  oneTimeCode: string;  // rotates each minute
  action: string;       // 'billing.charge', etc.
  txId: string;
  expires: number;      // epoch seconds
};

export async function generatePkPass(fields: PassFields): Promise<Buffer> {
  // Check if passkit-generator is available
  let Template: any;
  try {
    const pkg = await import("passkit-generator");
    Template = pkg.Template;
  } catch (error) {
    throw new Error("PKPass generation requires 'passkit-generator' package. Run: npm i passkit-generator");
  }

  const { PKPASS_TEAM_ID, PKPASS_PASS_TYPE_ID, PKPASS_CERT_P12, PKPASS_CERT_P12_PASSWORD } = process.env;
  if (!PKPASS_TEAM_ID || !PKPASS_PASS_TYPE_ID || !PKPASS_CERT_P12 || !PKPASS_CERT_P12_PASSWORD) {
    throw new Error("PKPass env missing");
  }

  const template = new Template("eventTicket", {
    passTypeIdentifier: PKPASS_PASS_TYPE_ID!,
    teamIdentifier: PKPASS_TEAM_ID!,
    organizationName: "LUKHΛS",
    description: "LUKHΛS ID Approval",
    backgroundColor: "rgb(0,0,0)",
    foregroundColor: "rgb(255,255,255)",
    labelColor: "rgb(200,200,200)"
  });

  // assets (place logos in repo)
  const assets = path.resolve(process.cwd(), "branding/assets/pkpass");
  try {
    const icon = await fs.readFile(path.join(assets, "icon.png"));
    const logo = await fs.readFile(path.join(assets, "logo.png"));
    template.images.add("icon.png", icon);
    template.images.add("logo.png", logo);
  } catch { /* optional */ }

  template.primaryFields.add({ key: "alias", label: "ΛiD", value: fields.alias });
  template.secondaryFields.add({ key: "action", label: "Action", value: fields.action });
  template.auxiliaryFields.add({ key: "code", label: "Code", value: fields.oneTimeCode });
  template.backFields.add({ key: "tx", label: "Transaction", value: fields.txId });
  template.backFields.add({ key: "exp", label: "Expires", value: new Date(fields.expires * 1000).toISOString() });

  template.setBarcode({ message: fields.txId, format: "PKBarcodeFormatQR", messageEncoding: "iso-8859-1" });

  const pass = template.createPass({
    serialNumber: fields.serialNumber,
    webServiceURL: undefined, // add later if you implement PassKit Web Service
    authenticationToken: undefined
  });

  pass.setCertificates(
    await fs.readFile(PKPASS_CERT_P12),
    PKPASS_CERT_P12_PASSWORD!,
    undefined // WWDR is embedded in lib; or pass custom chain if needed
  );

  const buf = await pass.asBuffer();
  return buf;
}
