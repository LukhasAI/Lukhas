export type ModelID =
  | "lukhas-core"
  | "openai:gpt-5-pro"
  | "perplexity:sonar"
  | "sora:video";

export type Skill =
  | "web.research"
  | "validate.facts"
  | "write.email"
  | "prompt.optimize"
  | "video.summarize"
  | "video.generate";

export type Capability = {
  id: ModelID;
  strengths: Skill[];
  costHint: "low" | "med" | "high";
  latencyHint: "low" | "med" | "high";
  maxTokensIn?: number;
  notes?: string;
};

export const CAPABILITIES: Capability[] = [
  { id: "perplexity:sonar", strengths: ["web.research"], costHint: "med", latencyHint: "low", notes: "Fast web+citations" },
  { id: "openai:gpt-5-pro", strengths: ["validate.facts", "write.email", "prompt.optimize", "video.summarize"], costHint: "high", latencyHint: "med" },
  { id: "sora:video", strengths: ["video.generate"], costHint: "high", latencyHint: "high", notes: "Text→video" },
  { id: "lukhas-core", strengths: ["prompt.optimize", "write.email"], costHint: "low", latencyHint: "low", notes: "Local/tenant-safe" },
];