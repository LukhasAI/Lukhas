export type ToolSchema = {
  type: "function";
  function: { name: string; description?: string; parameters?: unknown };
};

export interface LukhasOptions {
  baseUrl: string;
  apiKey?: string;
  timeoutMs?: number;
}

export class Lukhas {
  private base: string;
  private apiKey?: string;
  private timeout: number;

  constructor(opts: LukhasOptions) {
    this.base = opts.baseUrl.replace(/\/$/, "");
    this.apiKey = opts.apiKey;
    this.timeout = opts.timeoutMs ?? 10_000;
  }

  private async req(path: string, init?: RequestInit): Promise<any> {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort("timeout"), this.timeout);
    const headers: Record<string, string> = {
      "content-type": "application/json",
    };
    if (this.apiKey) headers["x-api-key"] = this.apiKey;

    try {
      const res = await fetch(this.base + path, {
        ...init,
        headers,
        signal: ctrl.signal,
      });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`${res.status} ${res.statusText} ${text}`);
      }
      const ctype = res.headers.get("content-type") ?? "";
      if (ctype.includes("application/json")) return await res.json();
      return await res.text();
    } finally {
      clearTimeout(id);
    }
  }

  // Feedback
  feedbackCard(body: {
    target_action_id: string;
    rating: number;
    note?: string;
    user_id?: string;
    tags?: string[];
  }) {
    return this.req("/feedback/card", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }
  feedbackLut() {
    return this.req("/feedback/lut");
  }

  // Tools
  toolsRegistry(): Promise<Record<string, ToolSchema>> {
    return this.req("/tools/registry");
  }
  async toolsNames(): Promise<{ tools: string[] }> {
    try {
      return await this.req("/tools/available");
    } catch (e) {
      return await this.req("/tools/names");
    }
  }
  toolSchema(toolName: string) {
    return this.req(`/tools/${encodeURIComponent(toolName)}`);
  }

  // DNA
  dnaHealth() {
    return this.req("/dna/health");
  }
  dnaCompare(key: string) {
    return this.req(`/dna/compare?key=${encodeURIComponent(key)}`);
  }

  // Admin
  adminSummary() {
    return this.req("/admin/summary.json");
  }

  // Helpers
  auditViewUrl(auditId: string) {
    return `${this.base}/audit/view/${encodeURIComponent(auditId)}`;
  }
}
