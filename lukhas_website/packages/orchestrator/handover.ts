import { CAPABILITIES, type ModelID, type Skill } from "./capabilities";
import { toProviderPrompt } from "./promptAdapter";
import type { ContextCapsule } from "./contextCapsule";

export type Hop = {
  from?: ModelID;
  to: ModelID;
  skill: Skill;
  costBudgetUSD?: number;
  latencyBudgetMs?: number;
};

function defaultCostBudget() {
  const v = Number(process.env.NEXT_PUBLIC_ORCH_DEFAULT_COST_BUDGET ?? "0.50");
  return isNaN(v) ? 0.5 : v;
}
function defaultTimeBudget() {
  const v = Number(process.env.NEXT_PUBLIC_ORCH_DEFAULT_TIME_BUDGET_MS ?? "30000");
  return isNaN(v) ? 30000 : v;
}

export async function suggestNextHops(
  goals: Skill[],
  capsule: ContextCapsule
): Promise<Hop[]> {
  const picks: Hop[] = [];
  for (const g of goals) {
    const candidates = CAPABILITIES.filter((c) => c.strengths.includes(g));
    // naive heuristic: prefer cheaper then faster
    const sorted = candidates.sort((a, b) => {
      const costRank = rank(a.costHint) - rank(b.costHint);
      if (costRank !== 0) return costRank;
      return rank(a.latencyHint) - rank(b.latencyHint);
    });
    const to = sorted[0]?.id;
    if (to) picks.push({ to, skill: g, costBudgetUSD: defaultCostBudget(), latencyBudgetMs: defaultTimeBudget() });
  }
  return picks;
}

export async function executeHop(h: Hop, capsule: ContextCapsule) {
  // Consent guard
  if (!capsule.consent.allowCrossProvider && h.to !== "lukhas-core") {
    throw new Error("Cross-provider sharing is disabled for this thread.");
  }
  // Build provider-specific prompt
  const prompt = toProviderPrompt(h.to, h.skill, capsule);
  // TODO: Integrate actual provider SDK calls here with redaction + headers.
  // For V1, return a stubbed result so UI can be built and tested.
  const output =
    h.skill === "validate.facts"
      ? "Validator: No critical contradictions detected. Confidence: 0.72"
      : h.skill === "video.summarize"
      ? "Storyboard: 6 scenes · Voiceover outline · Suggested Sora prompt"
      : "Draft output (stub) for " + h.to;
  return { model: h.to, prompt, output, evidence: [], durationMs: 1200, costUSD: 0.03 };
}

export async function validateWithGPT5(researchText: string, capsule: ContextCapsule) {
  const localCapsule: ContextCapsule = { ...capsule, excerpts: [researchText] };
  const prompt = toProviderPrompt("openai:gpt-5-pro", "validate.facts", localCapsule);
  // TODO: call provider and parse result
  return { verdict: "ok", issues: [] as string[], raw: prompt };
}

function rank(x: "low" | "med" | "high") {
  return x === "low" ? 0 : x === "med" ? 1 : 2;
}