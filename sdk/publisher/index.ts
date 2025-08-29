// Minimal Publisher SDK for rendering DAST widgets and NIAS clouds via the Delivery Engine

export type DeliveryMode = "cloud" | "widget";

export type Opportunity = {
  id: string;
  domain: string;
  title: string;
  description?: string;
  price_current?: number;
  price_alt?: number;
  affiliate?: { merchant: string; url: string; est_commission_bps: number };
  window: { start: number; end: number };
  risk?: { alignment?: number; stress_block?: boolean; notes?: string };
  economics?: { split_user_bps?: number; split_platform_bps?: number; tier?: string };
  media: { kind: "image" | "video"; cdn_url: string; alt: string };
  provenance: { sources: string[]; version: string; hash: string };
};

export interface PublisherSDKOpts {
  apiBase: string;             // https://api.lukhas.ai
  getUserState: () => Promise<{ stress?: number; driving?: boolean; hour?: number }>;
  token?: string;              // publisher key or user JWT
}

export class PublisherSDK {
  constructor(private opts: PublisherSDKOpts) {}

  async plan(intent: object, context: object, consent: object): Promise<Opportunity[]> {
    const res = await fetch(`${this.opts.apiBase}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(this.opts.token ? { "Authorization": `Bearer ${this.opts.token}` } : {}) },
      body: JSON.stringify({ intent, context, consent })
    });
    if (!res.ok) throw new Error(`plan failed: ${res.status}`);
    return res.json();
  }

  async deliver(op: Opportunity, mode: DeliveryMode): Promise<"rendered"|"blocked"|"queued"> {
    const user_state = await this.opts.getUserState();
    const res = await fetch(`${this.opts.apiBase}/deliver`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(this.opts.token ? { "Authorization": `Bearer ${this.opts.token}` } : {}) },
      body: JSON.stringify({ opportunity: op, mode, user_state })
    });
    if (!res.ok) throw new Error(`deliver failed: ${res.status}`);
    const payload = await res.json();
    return payload.status;
  }
}

// Simple NIAS cloud renderer (DOM-based example)
export function mountCloud(container: HTMLElement, op: Opportunity) {
  const wrap = document.createElement("div");
  wrap.style.position = "fixed";
  wrap.style.bottom = "24px";
  wrap.style.right = "24px";
  wrap.style.padding = "12px";
  wrap.style.borderRadius = "16px";
  wrap.style.boxShadow = "0 10px 30px rgba(0,0,0,0.2)";
  wrap.style.backdropFilter = "blur(8px)";
  wrap.style.background = "rgba(255,255,255,0.75)";

  const img = document.createElement("img");
  img.src = op.media.cdn_url;
  img.alt = op.media.alt;
  img.style.maxWidth = "200px";
  img.style.borderRadius = "12px";

  const title = document.createElement("div");
  title.textContent = op.title;
  title.style.marginTop = "8px";
  title.style.fontWeight = "600";

  const cta = document.createElement("a");
  cta.textContent = "Buy now";
  cta.href = op.affiliate?.url || "#";
  cta.target = "_blank";
  cta.rel = "noopener";
  cta.style.display = "inline-block";
  cta.style.marginTop = "8px";

  wrap.appendChild(img);
  wrap.appendChild(title);
  if (op.affiliate?.url) wrap.appendChild(cta);
  container.appendChild(wrap);
}

/*
// Publisher SDK quick usage example:

import { PublisherSDK, mountCloud } from "@lukhas/publisher-sdk";

const sdk = new PublisherSDK({
  apiBase: "https://api.lukhas.ai",
  getUserState: async () => ({ stress: 0.2, hour: new Date().getHours() }),
  token: localStorage.getItem("lukhas_pub_token") || undefined
});

const consent = { user_id: "u_42", scopes: ["amazon.orders.read"], ts: Date.now(), policy_version: "1.2.0", signature: "sig..." };

const ops = await sdk.plan({ type: "restock", item: "Acme Dog Food 10kg" }, { days_since_last: 28 }, consent);

// Attempt to render first opportunity as NIAS cloud
const status = await sdk.deliver(ops[0], "cloud");
if (status === "rendered") mountCloud(document.body, ops[0]);
*/