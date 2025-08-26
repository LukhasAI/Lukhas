// LUKHAS AI Token Estimation
// Estimate tokens and costs for different AI providers

const DEFAULT_RATES_PER_K: Record<string, number> = {
  // very rough placeholders; replace when you lock pricing
  "gpt-4o": 0.005,
  "gpt-4o-mini": 0.0015,
  "gpt-4-turbo": 0.01,
  "claude-3-opus": 0.015,
  "claude-3-sonnet": 0.008,
  "gemini-1.5-pro": 0.004,
  "gemini-1.5-flash": 0.001,
  lukhas: 0,
};

export function estimateTokens(text: string): number {
  // ~4 chars per token, with overhead
  return Math.max(60, Math.ceil(text.length / 4) + 80);
}

export function estimateCostUSD(tokens: number, model: string): number {
  const rate = DEFAULT_RATES_PER_K[model] ?? 0.005;
  return +((tokens / 1000) * rate).toFixed(4);
}

export function estimateTokensAndCost(text: string, model: string) {
  const tokens = estimateTokens(text);
  return { tokens, costUSD: estimateCostUSD(tokens, model) };
}
