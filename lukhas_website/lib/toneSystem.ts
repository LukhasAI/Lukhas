// LUKHAS AI Tone System
// Sentiment analysis and keyword-to-color/tempo mapping

const POSITIVE_WORDS =
  /(love|great|awesome|amazing|calm|peace|serene|happy|nice|cool|excited|fast|energetic|bright)/i;
const NEGATIVE_WORDS =
  /(sad|angry|slow|dark|bad|worse|worst|tired|heavy|cold|gloom|dull)/i;

export function sentimentScore(msg: string): number {
  const pos = msg.match(new RegExp(POSITIVE_WORDS, "gi"))?.length || 0;
  const neg = msg.match(new RegExp(NEGATIVE_WORDS, "gi"))?.length || 0;
  return Math.tanh((pos - neg) * 0.8); // [-1,1]
}

export function mapKeywordsToColorTempo(msg: string): {
  color?: string;
  tempo?: number;
} {
  const m = msg.toLowerCase();
  if (/love|heart|romance|passion/.test(m))
    return { color: "#ec4899", tempo: 1.15 };
  if (/calm|serene|breathe|meditat/.test(m))
    return { color: "#38bdf8", tempo: 0.75 };
  if (/focus|clarity|clean|minimal/.test(m))
    return { color: "#e5e7eb", tempo: 0.9 };
  if (/energy|hype|party|neon|glow|excited|fast/.test(m))
    return { color: "#a78bfa", tempo: 1.25 };
  if (/nature|grow|heal|guardian|safe|trust/.test(m))
    return { color: "#22c55e", tempo: 0.95 };
  if (/torus|donut/.test(m)) return { color: "#60a5fa", tempo: 1.05 };
  if (/cube|box/.test(m)) return { color: "#93c5fd", tempo: 0.9 };
  if (/sphere|orb|ball/.test(m)) return { color: "#e5e7eb", tempo: 1.0 };
  if (/helix|spiral|conscious/.test(m)) return { color: "#8b5cf6", tempo: 1.1 };
  return {};
}

export function threeLayerTone(
  poetic: string,
  friendly?: string,
  insight = "Legibility and convergence are prioritized; complex silhouettes are approximated before true assets are added."
): string {
  const f = friendly ?? "Say the word — I'll shape the field to match.";
  return `• Poetic: ${poetic}\n• Friendly: ${f}\n• Insight: ${insight}`;
}