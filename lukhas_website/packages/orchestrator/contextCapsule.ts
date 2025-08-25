export type ConsentFlags = {
  allowCrossProvider: boolean;
  allowExternalWebFetch: boolean;
  containPII: boolean;
  piiRedacted: boolean;
};

export type Evidence = { quote: string; source?: string; url?: string };

export type ContextCapsule = {
  threadId: string;
  summary: string;
  excerpts: string[];
  evidence?: Evidence[];
  userIntents: string[]; // e.g. ["validate.facts","video.generate"]
  consent: ConsentFlags;
  hash: string; // Λ-trace integrity stub
};