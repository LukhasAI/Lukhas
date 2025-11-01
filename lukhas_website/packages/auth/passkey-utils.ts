import type { Passkey } from './database'
import type { PasskeyCredential } from '../../../packages/auth/types/auth.types'

const DEFAULT_AAGUID = '00000000-0000-0000-0000-000000000000'

const toBase64Url = (value: Uint8Array): string =>
  Buffer.from(value)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '')

const normalizeBase64Url = (value: string): string =>
  value.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')

const toISOString = (value?: Date): string => {
  if (!value) {
    return new Date().toISOString()
  }

  return value instanceof Date ? value.toISOString() : new Date(value).toISOString()
}

export const mapPasskeyToCredential = (passkey: Passkey): PasskeyCredential => {
  const credentialId = passkey.credential_id_b64
    ? normalizeBase64Url(passkey.credential_id_b64)
    : toBase64Url(passkey.credential_id)

  const publicKey = Buffer.from(passkey.public_key).toString('base64')

  const createdAt = toISOString(passkey.created_at)
  const lastUsedAt = toISOString(passkey.last_used_at ?? passkey.created_at)

  const authenticatorInfo =
    passkey.device_label && (passkey.device_type === 'platform' || passkey.device_type === 'cross-platform')
      ? {
          name: passkey.device_label,
          vendor: 'Unknown',
          type: passkey.device_type,
          trusted: false as const
        }
      : undefined

  return {
    id: credentialId,
    publicKey,
    algorithm: passkey.algorithm,
    aaguid: passkey.aaguid || DEFAULT_AAGUID,
    authenticatorInfo,
    signCount: passkey.sign_count,
    uvInitialized: passkey.uv_required,
    backupEligible: passkey.backup_eligible,
    backupState: passkey.backup_state,
    deviceType: passkey.device_type,
    createdAt,
    lastUsedAt
  }
}
