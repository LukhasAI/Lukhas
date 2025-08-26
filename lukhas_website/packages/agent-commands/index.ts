import type { ContextCapsule } from "@lukhas/orchestrator/contextCapsule";
import { suggestNextHops, executeHop } from "@lukhas/orchestrator/handover";

export type CmdId =
  | "validate"
  | "storyboard"
  | "gen-video"
  | "optimize-prompts"
  | "write-email"
  | "connect-gmail"
  | "toggle-consent"
  | "new-thread";

export type Command = {
  id: CmdId;
  title: string;
  hint?: string;
  run: (ctx: { capsule?: ContextCapsule; emit: (r: { title: string; body: string; kind?: string; model?: string }) => void }) => Promise<void>;
  featured?: boolean; // show in mini palette
};

export function registry(): Command[] {
  return [
    {
      id: "validate",
      title: "Validate with GPT-5 Pro",
      hint: "Fact check the current answer",
      featured: true,
      async run({ capsule, emit }) {
        if (!capsule) return;
        const hops = await suggestNextHops(["validate.facts"] as any, capsule);
        if (!hops[0]) return;
        const r = await executeHop(hops[0], capsule);
        emit({ title: "Validation · Facts checked", body: r.output, kind: "validation", model: r.model });
      },
    },
    {
      id: "storyboard",
      title: "Summarize to storyboard",
      hint: "Create a 6-scene plan for Sora",
      featured: true,
      async run({ capsule, emit }) {
        if (!capsule) return;
        const hops = await suggestNextHops(["video.summarize"] as any, capsule);
        if (!hops[0]) return;
        const r = await executeHop(hops[0], capsule);
        emit({ title: "Storyboard · Video plan", body: r.output, kind: "storyboard", model: r.model });
      },
    },
    {
      id: "gen-video",
      title: "Generate video (Sora)",
      hint: "Text→video handoff",
      async run({ capsule, emit }) {
        if (!capsule) return;
        const hops = await suggestNextHops(["video.generate"] as any, capsule);
        if (!hops[0]) return;
        const r = await executeHop(hops[0], capsule);
        emit({ title: "Video · Generation request", body: r.output, kind: "text", model: r.model });
      },
    },
    {
      id: "optimize-prompts",
      title: "Optimize prompts (meta)",
      hint: "Make prompts better for other models",
      featured: true,
      async run({ capsule, emit }) {
        if (!capsule) return;
        const hops = await suggestNextHops(["prompt.optimize"] as any, capsule);
        if (!hops[0]) return;
        const r = await executeHop(hops[0], capsule);
        emit({ title: "Prompt · Optimized", body: r.output, kind: "text", model: r.model });
      },
    },
    {
      id: "write-email",
      title: "Draft reply (email)",
      hint: "Polymorphic composer will open",
      featured: true,
      async run() {
        // tell Studio footer to switch to email mode and insert a draft
        const draft = "Subject: Re: …\n\nHi …,\n\nThanks for reaching out. Here's a quick summary: …\n\nBest,\n—";
        document.dispatchEvent(new CustomEvent("lukhas:composer-email", { detail: { body: draft } }));
      },
    },
    {
      id: "connect-gmail",
      title: "Connect Gmail…",
      hint: "Enable inbox unificado",
      async run() { window.location.href = "/settings/integrations#gmail"; },
    },
    {
      id: "toggle-consent",
      title: "Toggle cross-provider consent",
      hint: "Enable/disable sharing across models",
      async run() { document.dispatchEvent(new CustomEvent("lukhas:toggle-consent")); },
    },
    {
      id: "new-thread",
      title: "New Studio thread",
      hint: "Create a fresh workspace",
      async run() { window.location.href = "/studio/new"; },
    },
  ];
}
