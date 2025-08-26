-- Begin atomic migration
BEGIN;

-- Enums
DO $$ BEGIN
  CREATE TYPE "IdentifierType" AS ENUM ('email','phone','other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE "ChallengeType" AS ENUM ('grid','swipe','sequence','oddOneOut','wordPair');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE "Role" AS ENUM ('owner','admin','developer','analyst','viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Users
CREATE TABLE IF NOT EXISTS "User" (
  "id"              VARCHAR(40) PRIMARY KEY, -- lid_<ULID>
  "createdAt"       TIMESTAMPTZ NOT NULL DEFAULT now(),
  "updatedAt"       TIMESTAMPTZ NOT NULL DEFAULT now(),
  "displayName"     VARCHAR(120),
  "tier"            VARCHAR NOT NULL DEFAULT 'free',
  "locale"          VARCHAR(8)
);

-- Auto-update updatedAt
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW."updatedAt" = now(); RETURN NEW; END; $$ LANGUAGE plpgsql;
DO $$ BEGIN
  CREATE TRIGGER trg_user_updated_at BEFORE UPDATE ON "User"
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Verified identifiers (email/phone/other) - NOT public
CREATE TABLE IF NOT EXISTS "VerifiedIdentifier" (
  "id"             VARCHAR(36) PRIMARY KEY,
  "userId"         VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "type"           "IdentifierType" NOT NULL,
  "valueHash"      VARCHAR(128) NOT NULL,
  "valueNorm"      VARCHAR(320) NOT NULL,
  "provider"       VARCHAR(80),
  "verifiedAt"     TIMESTAMPTZ,
  "primary"        BOOLEAN NOT NULL DEFAULT FALSE,
  "createdAt"      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_identifier_type_valuehash ON "VerifiedIdentifier" ("type","valueHash");
CREATE INDEX IF NOT EXISTS ix_identifier_user_type ON "VerifiedIdentifier" ("userId","type");

-- Public alias mapping (no PII)
CREATE TABLE IF NOT EXISTS "LidAlias" (
  "id"            VARCHAR(36) PRIMARY KEY,
  "userId"        VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "aliasKey"      VARCHAR(64) NOT NULL,
  "aliasDisplay"  VARCHAR(128) NOT NULL,
  "realm"         VARCHAR(12) NOT NULL,
  "zone"          VARCHAR(3)  NOT NULL,
  "idType"        "IdentifierType" NOT NULL,
  "verifiedAt"    TIMESTAMPTZ,
  "createdAt"     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_lidalias_key ON "LidAlias" ("aliasKey");
CREATE INDEX IF NOT EXISTS ix_lidalias_user ON "LidAlias" ("userId");

-- WebAuthn passkeys
CREATE TABLE IF NOT EXISTS "PasskeyCredential" (
  "id"            VARCHAR(36) PRIMARY KEY,
  "userId"        VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "credentialId"  BYTEA NOT NULL UNIQUE,
  "publicKey"     BYTEA NOT NULL,
  "aaguid"        VARCHAR(64),
  "transports"    VARCHAR(64),
  "signCount"     INT NOT NULL DEFAULT 0,
  "deviceBinding" VARCHAR(64),
  "createdAt"     TIMESTAMPTZ NOT NULL DEFAULT now(),
  "lastUsedAt"    TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_passkey_user ON "PasskeyCredential" ("userId");

-- Refresh token families & tokens (reuse detection)
CREATE TABLE IF NOT EXISTS "RefreshTokenFamily" (
  "id"            VARCHAR(36) PRIMARY KEY,
  "userId"        VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "familyId"      VARCHAR(64) NOT NULL,
  "currentId"     VARCHAR(64) NOT NULL,
  "reuseDetected" TIMESTAMPTZ,
  "revokedAt"     TIMESTAMPTZ,
  "createdAt"     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_rtf_user_family ON "RefreshTokenFamily" ("userId","familyId");

CREATE TABLE IF NOT EXISTS "RefreshToken" (
  "id"            VARCHAR(36) PRIMARY KEY,
  "familyId"      VARCHAR(36) NOT NULL REFERENCES "RefreshTokenFamily"("id") ON DELETE CASCADE,
  "tokenId"       VARCHAR(64) NOT NULL,
  "rotatedAt"     TIMESTAMPTZ,
  "revokedAt"     TIMESTAMPTZ,
  "ipHash"        VARCHAR(64),
  "uaHash"        VARCHAR(64),
  "deviceId"      VARCHAR(64),
  "createdAt"     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_rt_family_token ON "RefreshToken" ("familyId","tokenId");

-- Emoji/word secret (Argon2id hash + salt)
CREATE TABLE IF NOT EXISTS "EmojiSecret" (
  "id"          VARCHAR(36) PRIMARY KEY,
  "userId"      VARCHAR(40) NOT NULL UNIQUE REFERENCES "User"("id") ON DELETE CASCADE,
  "secretHash"  VARCHAR(256) NOT NULL,
  "salt"        BYTEA NOT NULL,
  "enabled"     BOOLEAN NOT NULL DEFAULT TRUE,
  "createdAt"   TIMESTAMPTZ NOT NULL DEFAULT now(),
  "rotatedAt"   TIMESTAMPTZ
);

-- Ephemeral challenges
CREATE TABLE IF NOT EXISTS "GridChallenge" (
  "id"          VARCHAR(36) PRIMARY KEY,
  "userId"      VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "type"        "ChallengeType" NOT NULL,
  "payloadHash" VARCHAR(128) NOT NULL,
  "issuedAt"    TIMESTAMPTZ NOT NULL DEFAULT now(),
  "expiresAt"   TIMESTAMPTZ NOT NULL,
  "tries"       INT NOT NULL DEFAULT 0,
  "consumedAt"  TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_challenge_user_exp ON "GridChallenge" ("userId","expiresAt");

-- Guardians for social recovery
CREATE TABLE IF NOT EXISTS "Guardian" (
  "id"         VARCHAR(36) PRIMARY KEY,
  "userId"     VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "type"       "IdentifierType" NOT NULL,
  "contact"    VARCHAR(320) NOT NULL,
  "publicKey"  TEXT,
  "addedAt"    TIMESTAMPTZ NOT NULL DEFAULT now(),
  "revokedAt"  TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_guardian_user_contact ON "Guardian" ("userId","contact");

-- Recovery tickets & approvals
CREATE TABLE IF NOT EXISTS "RecoveryTicket" (
  "id"               UUID PRIMARY KEY,
  "userId"           VARCHAR(40) NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "state"            VARCHAR(16) NOT NULL,  -- 'open','approved','completed','expired'
  "requiredApprovals" INT NOT NULL DEFAULT 0,
  "approvalsCount"    INT NOT NULL DEFAULT 0,
  "reason"           VARCHAR(24) NOT NULL,  -- 'lost_device','compromised','other'
  "createdAt"        TIMESTAMPTZ NOT NULL DEFAULT now(),
  "expiresAt"        TIMESTAMPTZ NOT NULL,
  "meta"             JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS ix_recovery_user_time ON "RecoveryTicket" ("userId","createdAt");

CREATE TABLE IF NOT EXISTS "RecoveryApproval" (
  "id"         VARCHAR(36) PRIMARY KEY,
  "ticketId"   UUID NOT NULL REFERENCES "RecoveryTicket"("id") ON DELETE CASCADE,
  "guardianId" VARCHAR(36),
  "channel"    VARCHAR(16) NOT NULL, -- 'email','phone','guardian','admin'
  "approved"   BOOLEAN NOT NULL,
  "createdAt"  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT fk_rec_app_guardian FOREIGN KEY ("guardianId") REFERENCES "Guardian"("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_recovery_approval_ticket ON "RecoveryApproval" ("ticketId");

-- Security events
CREATE TABLE IF NOT EXISTS "SecurityEvent" (
  "id"         VARCHAR(36) PRIMARY KEY,
  "userId"     VARCHAR(40),
  "kind"       VARCHAR(64) NOT NULL,
  "meta"       JSONB NOT NULL DEFAULT '{}'::jsonb,
  "createdAt"  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT fk_se_user FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_se_user_time ON "SecurityEvent" ("userId","createdAt");

-- Onboarding sessions (ephemeral)
CREATE TABLE IF NOT EXISTS "OnboardingSession" (
  "id"           UUID PRIMARY KEY,
  "realm"        VARCHAR(12) NOT NULL,
  "zone"         VARCHAR(3)  NOT NULL,
  "idType"       "IdentifierType" NOT NULL,
  "identifierNorm" VARCHAR(320) NOT NULL,
  "codeHash"     VARCHAR(128) NOT NULL,
  "attempts"     INT NOT NULL DEFAULT 0,
  "createdAt"    TIMESTAMPTZ NOT NULL DEFAULT now(),
  "expiresAt"    TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_onboard_identifier ON "OnboardingSession" ("identifierNorm");

COMMIT;
