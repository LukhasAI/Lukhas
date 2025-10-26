export function normalizeEmail(s: string) {
  return s.trim().toLowerCase();
}

// TODO: replace with libphonenumber; for now simple E.164-like
export function normalizePhoneE164(s: string) {
  return s.replace(/[^\d+]/g,'');
}