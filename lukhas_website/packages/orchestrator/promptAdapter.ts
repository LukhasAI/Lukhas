import type { ModelID, Skill } from "./capabilities";
import type { ContextCapsule } from "./contextCapsule";

export function toProviderPrompt(
  model: ModelID,
  skill: Skill,
  capsule: ContextCapsule
): { system: string; user: string } {
  const base =
    `Task: ${capsule.summary}\n` +
    `Intents: ${capsule.userIntents.join(", ")}\n` +
    `Use ONLY these excerpts:\n` +
    capsule.excerpts.map((e, i) => `[${i + 1}] ${e}`).join("\n");

  if (model.startsWith("perplexity")) {
    return {
      system: "Answer with citations only. If unsure, say so.",
      user: base + "\nReturn top-3 sources with URLs.",
    };
  }
  if (model.startsWith("openai:gpt-5-pro")) {
    const sys =
      skill === "validate.facts"
        ? "Be a ruthless verifier. Explicitly list contradictions and confidence."
        : "Be clear, structured, and concise.";
    return { system: sys, user: base };
  }
  if (model.startsWith("sora")) {
    return {
      system: "Generate a cinematic plan",
      user: base + "\nOutput: 60s video plan + clean text prompt.\nNo unsafe content.",
    };
  }
  return { system: "Optimize prompts and prepare handoffs.", user: base };
}
