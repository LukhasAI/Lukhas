import { 
  createFamily, 
  issueRefreshDB, 
  markUsed, 
  isFamilyRevoked,
  revokeFamily,
  rotateRefreshTokenSecure 
} from '../refresh-store';

describe('Refresh Token Store', () => {
  const userId = 'test-user-' + Date.now();

  test('creates new token family', async () => {
    const familyId = await createFamily(userId);
    expect(familyId).toBeTruthy();
    expect(typeof familyId).toBe('string');
  });

  test('issues refresh token in family', async () => {
    const result = await issueRefreshDB({ 
      userId, 
      ttlDays: 30,
      deviceId: 'test-device',
      ip: '127.0.0.1'
    });
    
    expect(result.familyId).toBeTruthy();
    expect(result.jti).toBeTruthy();
    expect(result.tokenId).toBeTruthy();
  });

  test('detects and handles token reuse', async () => {
    // Issue a new token
    const { familyId, jti } = await issueRefreshDB({ 
      userId, 
      ttlDays: 30 
    });
    
    // First use should succeed
    const firstUse = await markUsed(jti);
    expect(firstUse.ok).toBe(true);
    expect(firstUse.familyId).toBe(familyId);
    expect(firstUse.userId).toBe(userId);
    
    // Second use should fail (reuse detected)
    const secondUse = await markUsed(jti);
    expect(secondUse.ok).toBe(false);
    expect(secondUse.reason).toBe('reuse_detected');
    
    // Family should be revoked
    const isRevoked = await isFamilyRevoked(familyId);
    expect(isRevoked).toBe(true);
  });

  test('rotates refresh token securely', async () => {
    // Issue initial token
    const initial = await issueRefreshDB({ 
      userId, 
      ttlDays: 30,
      deviceId: 'test-device'
    });
    
    // Rotate the token
    const rotated = await rotateRefreshTokenSecure(
      initial.jti,
      'test-device',
      '127.0.0.1',
      'jest-test'
    );
    
    expect(rotated.error).toBeUndefined();
    expect(rotated.access).toBeTruthy();
    expect(rotated.refresh?.jti).toBeTruthy();
    expect(rotated.refresh?.familyId).toBe(initial.familyId);
    
    // Old token should not be usable again
    const reuseAttempt = await markUsed(initial.jti);
    expect(reuseAttempt.ok).toBe(false);
    expect(reuseAttempt.reason).toBe('reuse_detected');
  });

  test('handles missing token gracefully', async () => {
    const result = await markUsed('non-existent-jti');
    expect(result.ok).toBe(false);
    expect(result.reason).toBe('not_found');
  });

  test('revokes entire family on demand', async () => {
    // Create family with tokens
    const { familyId, jti } = await issueRefreshDB({ 
      userId, 
      ttlDays: 30 
    });
    
    // Revoke the family
    await revokeFamily(familyId, 'user_logout');
    
    // Check family is revoked
    const isRevoked = await isFamilyRevoked(familyId);
    expect(isRevoked).toBe(true);
    
    // Token should not be usable
    const useAttempt = await markUsed(jti);
    expect(useAttempt.ok).toBe(false);
  });

  test('handles expired tokens', async () => {
    // Issue token with 0 days TTL (expires immediately)
    const { jti } = await issueRefreshDB({ 
      userId, 
      ttlDays: 0 
    });
    
    // Wait a bit to ensure expiration
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Should fail due to expiration
    const result = await markUsed(jti);
    expect(result.ok).toBe(false);
    expect(result.reason).toBe('expired');
  });
});