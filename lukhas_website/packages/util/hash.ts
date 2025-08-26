import crypto from 'crypto';

export function hmacSHA256(input: string, secret: string) {
  return crypto.createHmac('sha256', secret).update(input).digest('hex');
}

export function sha256b64(input: string) {
  return crypto.createHash('sha256').update(input).digest('base64url');
}
