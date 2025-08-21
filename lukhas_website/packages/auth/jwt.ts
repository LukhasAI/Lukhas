import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';

const ACCESS_TTL_MIN = parseInt(process.env.AUTH_ACCESS_TTL_MINUTES || '15', 10);
const REFRESH_TTL_DAYS = parseInt(process.env.AUTH_REFRESH_TTL_DAYS || '30', 10);

const privJwk = JSON.parse(process.env.AUTH_JWT_PRIVATE_JWK || '{}');
const pubSet  = JSON.parse(process.env.AUTH_JWKS_JSON || '[]');

function signRS256(payload: any, ttlSec: number) {
  const kid = privJwk.kid;
  return jwt.sign(payload, privJwk as any, { algorithm: 'RS256', expiresIn: ttlSec, keyid: kid });
}

export async function issueAccessToken(claims: { sub: string; [k: string]: any }) {
  return signRS256({ ...claims, typ: 'access' }, ACCESS_TTL_MIN * 60);
}

export async function issueRefreshToken({ sub, deviceId, familyId }: { sub: string; deviceId?: string; familyId?: string }) {
  const fid = familyId || randomUUID();
  const jti = randomUUID();
  // TODO: persist { jti, fid, sub, deviceId, exp } in DB
  const token = signRS256({ sub, typ: 'refresh', fid, jti, deviceId }, REFRESH_TTL_DAYS * 24 * 3600);
  return { token, familyId: fid, jti };
}

export async function rotateRefreshToken({ token }: { token: string }) {
  // TODO: verify, mark old jti as used, revoke family on reuse, issue new one
  return { token: 'NEW_REFRESH_TOKEN', familyId: 'FAMILY', jti: 'JTI' };
}

export async function verifyAccessToken(token: string) {
  try {
    const payload = jwt.verify(token, privJwk as any, { algorithms: ['RS256'] });
    return { valid: true, payload };
  } catch (error) {
    return { valid: false, error };
  }
}
