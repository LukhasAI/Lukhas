// LUKHAS AI Safety System
// Violence detection and calm defaults

const VIOLENT_WORDS = /(kill|murder|death|destroy|violence|attack|harm|hurt|weapon|gun|knife|bomb|war|fight|blood|pain)/i

export function isViolent(msg: string): boolean {
  return VIOLENT_WORDS.test(msg.toLowerCase())
}

export const calmDefaults = {
  accentColor: '#38bdf8', // Calm blue
  tempo: 0.75,            // Slower tempo
  morphSpeed: 0.018       // Gentle morphing
}