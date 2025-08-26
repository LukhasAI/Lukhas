import { z } from 'zod';

export const StartOnboarding = z.object({
  realm: z.string().min(2).max(12).regex(/^[A-Z0-9-]+$/i),
  zone:  z.string().min(2).max(3).regex(/^[A-Z]+$/i),
  identifier: z.string().min(3).max(320),
  idType: z.enum(['email','phone','other']),
  locale: z.string().optional()
});

export const VerifyOnboarding = z.object({
  onboardingId: z.string().uuid(),
  code: z.string().min(4).max(8),
});

export const BindAlias = z.object({
  realm: z.string(),
  zone: z.string(),
  identifier: z.string(),
  idType: z.enum(['email','phone','other'])
});

export const CreateChallenge = z.object({
  type: z.enum(['grid','swipe','sequence','oddOneOut','wordPair']).optional(),
  risk: z.object({ score: z.number().min(0).max(100) }).optional()
});

export const VerifyChallenge = z.object({
  challengeId: z.string(),
  response: z.any() // e.g., ordered emoji IDs or yes/no vector; server verifies
});

export const RecoveryInit = z.object({
  reason: z.enum(['lost_device','compromised','other']),
  channel: z.enum(['email','phone','guardian']).optional()
});

export const RecoveryGuardianApprove = z.object({
  ticketId: z.string().uuid(),
  approve: z.boolean()
});

export const RecoveryComplete = z.object({
  ticketId: z.string().uuid(),
  method: z.enum(['backup_codes','guardians','hardware_key','oob']),
});

// Type exports
export type StartOnboardingData = z.infer<typeof StartOnboarding>;
export type VerifyOnboardingData = z.infer<typeof VerifyOnboarding>;
export type BindAliasData = z.infer<typeof BindAlias>;
export type CreateChallengeData = z.infer<typeof CreateChallenge>;
export type VerifyChallengeData = z.infer<typeof VerifyChallenge>;
export type RecoveryInitData = z.infer<typeof RecoveryInit>;
export type RecoveryGuardianApproveData = z.infer<typeof RecoveryGuardianApprove>;
export type RecoveryCompleteData = z.infer<typeof RecoveryComplete>;
