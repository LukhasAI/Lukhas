process.env.TS_NODE_COMPILER_OPTIONS = JSON.stringify({
  module: 'commonjs',
  moduleResolution: 'node',
  esModuleInterop: true
})

const { register } = require('ts-node')

register({
  transpileOnly: true
})

const assert = require('node:assert/strict')
const { mapPasskeyToCredential } = require('../../packages/auth/passkey-utils.ts')

const basePasskey = {
  id: 'pk-1',
  created_at: new Date('2023-01-01T00:00:00Z'),
  updated_at: undefined,
  deleted_at: undefined,
  user_id: 'user-1',
  credential_id: Uint8Array.from([1, 2, 3]),
  credential_id_b64: 'AQID',
  public_key: Uint8Array.from([4, 5, 6]),
  algorithm: -7,
  user_handle: 'handle',
  aaguid: 'test-aaguid',
  device_type: 'platform',
  device_label: 'Test Device',
  sign_count: 10,
  uv_required: true,
  rk: true,
  transports: ['internal'],
  attestation_type: undefined,
  attestation_data: undefined,
  backup_eligible: true,
  backup_state: false,
  last_used_at: new Date('2024-01-01T00:00:00Z'),
  use_count: 3
}

const scenarios = [
  {
    name: 'normalizes credential metadata with stored identifiers',
    passkey: basePasskey,
    expectations: result => {
      assert.equal(result.id, 'AQID')
      assert.equal(result.publicKey, 'BAUG')
      assert.equal(result.algorithm, -7)
      assert.equal(result.aaguid, 'test-aaguid')
      assert.deepEqual(result.authenticatorInfo, {
        name: 'Test Device',
        vendor: 'Unknown',
        type: 'platform',
        trusted: false
      })
      assert.equal(result.signCount, 10)
      assert.equal(result.uvInitialized, true)
      assert.equal(result.backupEligible, true)
      assert.equal(result.backupState, false)
      assert.equal(result.deviceType, 'platform')
      assert.equal(result.createdAt, basePasskey.created_at.toISOString())
      assert.equal(result.lastUsedAt, basePasskey.last_used_at.toISOString())
    }
  },
  {
    name: 'derives identifiers when optional fields are absent',
    passkey: {
      ...basePasskey,
      id: 'pk-2',
      created_at: new Date('2023-06-01T00:00:00Z'),
      credential_id: Uint8Array.from([9, 8, 7, 6]),
      credential_id_b64: '',
      public_key: Uint8Array.from([10, 11, 12, 13]),
      algorithm: -257,
      aaguid: undefined,
      device_type: 'unknown',
      device_label: '',
      sign_count: 0,
      uv_required: false,
      backup_eligible: false,
      backup_state: false,
      last_used_at: undefined,
      use_count: 0
    },
    expectations: result => {
      assert.equal(result.id, 'CQgHBg')
      assert.equal(result.publicKey, 'CgsMDQ==')
      assert.equal(result.aaguid, '00000000-0000-0000-0000-000000000000')
      assert.equal(result.authenticatorInfo, undefined)
      assert.equal(result.lastUsedAt, new Date('2023-06-01T00:00:00Z').toISOString())
    }
  }
]

scenarios.forEach(({ name, passkey, expectations }) => {
  const result = mapPasskeyToCredential(passkey)
  try {
    expectations(result)
    console.log(`✔ ${name}`)
  } catch (error) {
    console.error(`✖ ${name}`)
    throw error
  }
})
