export type QrgClaims = {
  v: 'qrg/v1';
  iss: 'lukhas';
  aud: 'lid';
  sub: string;     // lid_<ULID>
  tx:  string;     // txId
  scope: string;   // e.g., 'api.keys.create'
  nonce: string;   // base64url 32B
  iat: number;     // unix seconds
  exp: number;     // unix seconds
};