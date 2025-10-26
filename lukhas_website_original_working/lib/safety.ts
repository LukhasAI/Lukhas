// LUKHAS AI Safety System
// Violence detection and calm defaults

export const VIOLENCE_WORDS =
  /(kill|hurt|attack|violence|explode|blood|murder|assault|shoot|stab|rage|torture|suicide)/i;

export function isViolent(text: string): boolean {
  return VIOLENCE_WORDS.test(text);
}

export const calmDefaults = {
  accentColor: "#38bdf8",
  tempo: 0.75,
  morphSpeed: 0.018,
};