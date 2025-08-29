// Minimal Merchant SDK for NIAS/DAST Opportunity campaigns
// Usage: a merchant integrates this to push creatives + track attribution.

export type AffiliateLink = { merchant: string; url: string; est_commission_bps: number };

export type Creative = {
  id: string;
  kind: "image" | "video";
  cdn_url: string;
  alt: string;
  // optional brand-safe metadata
  width?: number;
  height?: number;
  hash?: string;
};

export type Campaign = {
  id: string;
  domain: string;               // e.g., "retail.pet_food"
  title: string;                // "Time to restock?"
  description?: string;
  price_current?: number;
  price_alt?: number;
  affiliate?: AffiliateLink;    // optional; omit if you use S2S only
  creatives: Creative[];        // at least one
  window?: { start: number; end: number }; // optional suggested window
  provenance?: { sources: string[]; version?: string; hash?: string };
};

export type AttributionEvent = {
  opportunity_id: string;
  user_id?: string;             // optional (pseudonymous)
  click_id?: string;
  order_id?: string;
  sku?: string;
  price: number;
  currency: string;
  ts: number;                   // epoch ms
  meta?: Record<string, unknown>;
};

export interface MerchantSDKOpts {
  apiBase: string;              // https://api.lukhas.ai
  apiKey: string;               // merchant-specific
}

export class MerchantSDK {
  constructor(private opts: MerchantSDKOpts) {}

  async createCampaign(c: Campaign): Promise<{ id: string }> {
    const res = await fetch(`${this.opts.apiBase}/merchant/campaigns`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.opts.apiKey}` },
      body: JSON.stringify(c),
    });
    if (!res.ok) throw new Error(`createCampaign failed: ${res.status}`);
    return res.json();
  }

  async uploadCreative(file: Blob, meta: Omit<Creative, "cdn_url">): Promise<Creative> {
    // presigned URL flow recommended; this is a placeholder
    const res = await fetch(`${this.opts.apiBase}/merchant/creatives/upload`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${this.opts.apiKey}` },
      body: file
    });
    if (!res.ok) throw new Error(`uploadCreative failed: ${res.status}`);
    const { cdn_url } = await res.json();
    return { ...meta, cdn_url };
  }

  async registerAffiliateLink(campaignId: string, link: AffiliateLink): Promise<void> {
    const res = await fetch(`${this.opts.apiBase}/merchant/campaigns/${campaignId}/affiliate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.opts.apiKey}` },
      body: JSON.stringify(link),
    });
    if (!res.ok) throw new Error(`registerAffiliateLink failed: ${res.status}`);
  }

  // Server-to-server postback for robust attribution
  async reportAttribution(evt: AttributionEvent): Promise<{ settled: boolean }> {
    const res = await fetch(`${this.opts.apiBase}/merchant/attribution`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${this.opts.apiKey}` },
      body: JSON.stringify(evt),
    });
    if (!res.ok) throw new Error(`reportAttribution failed: ${res.status}`);
    return res.json();
  }
}

/*
// Merchant SDK quick usage example:

import { MerchantSDK } from "@lukhas/merchant-sdk";

const sdk = new MerchantSDK({ apiBase: "https://api.lukhas.ai", apiKey: process.env.MERCHANT_API_KEY! });

const creative = await sdk.uploadCreative(myPngBlob, { id: "dogfood_hero", kind: "image", alt: "Dog food bag on kitchen floor" });

const campaign = await sdk.createCampaign({
  id: "acme_dogfood_august",
  domain: "retail.pet_food",
  title: "Time to restock?",
  price_current: 39.90,
  creatives: [creative],
  affiliate: { merchant: "Acme Pets", url: "https://merchant.com/aff?c=...", est_commission_bps: 1200 },
  provenance: { sources: ["merchant:acme"], version: "1.0.0", hash: "sha256:..." }
});
*/