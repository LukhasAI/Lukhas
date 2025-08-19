// LUKHAS AI Token Estimation
// Estimate tokens and costs for different AI providers

interface TokenEstimate {
  tokens: number
  costUSD: number
}

// Rough token estimation (1 token ≈ 4 characters for most models)
function estimateTokens(text: string): number {
  return Math.max(60, Math.ceil(text.length / 4) + 80) // Base + response overhead
}

// Cost rates per 1K tokens (approximate, as of 2024)
const COST_RATES: Record<string, number> = {
  'lukhas': 0,
  'gpt-4o': 0.005,
  'gpt-4o-mini': 0.0015,
  'gpt-4-turbo': 0.01,
  'gpt-4': 0.03,
  'claude-3-opus': 0.015,
  'claude-3-sonnet': 0.003,
  'claude-3-haiku': 0.00025,
  'gemini-1.5-pro': 0.0035,
  'gemini-1.5-flash': 0.0005,
  'pplx-7b-online': 0.0007,
  'pplx-70b-online': 0.001
}

export function estimateTokensAndCost(text: string, model: string): TokenEstimate {
  const tokens = estimateTokens(text)
  const rate = COST_RATES[model] || 0.005 // Default fallback rate
  const costUSD = Number(((tokens / 1000) * rate).toFixed(6))
  
  return { tokens, costUSD }
}