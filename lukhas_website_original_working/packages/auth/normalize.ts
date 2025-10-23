/**
 * Normalize an email address for consistent storage and comparison
 */
export function normalizeEmail(email: string): string {
  // Convert to lowercase and trim whitespace
  let normalized = email.toLowerCase().trim();
  
  // Handle Gmail plus addressing and dots
  const [localPart, domain] = normalized.split('@');
  if (domain === 'gmail.com' || domain === 'googlemail.com') {
    // Remove dots and everything after + in Gmail addresses
    const cleanLocal = localPart.split('+')[0].replace(/\./g, '');
    normalized = `${cleanLocal}@gmail.com`;
  }
  
  return normalized;
}

/**
 * Normalize a phone number to E.164 format
 * Note: This is a basic implementation. Consider using libphonenumber for production
 */
export function normalizePhoneE164(phone: string): string {
  // Remove all non-digit characters
  let digits = phone.replace(/\D/g, '');
  
  // Handle US numbers (10 digits without country code)
  if (digits.length === 10) {
    digits = '1' + digits;
  }
  
  // Ensure it starts with + for E.164
  if (!digits.startsWith('1') && digits.length === 11) {
    // Assume US number with country code
    return '+' + digits;
  }
  
  // For international numbers, just clean and add +
  if (digits.length > 10) {
    return '+' + digits;
  }
  
  // Return as-is if we can't normalize
  return '+' + digits;
}

/**
 * Normalize a username (alphanumeric + underscore, case-insensitive)
 */
export function normalizeUsername(username: string): string {
  return username.toLowerCase().trim().replace(/[^a-z0-9_]/g, '');
}