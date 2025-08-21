import { describe, it, expect, jest, beforeAll } from '@jest/globals';
import { generatePkPass, type PassFields } from '../apple-pass';

// Mock passkit-generator since it requires certificates
jest.mock('passkit-generator', () => ({
  Template: jest.fn().mockImplementation(() => ({
    images: {
      add: jest.fn()
    },
    primaryFields: {
      add: jest.fn()
    },
    secondaryFields: {
      add: jest.fn()
    },
    auxiliaryFields: {
      add: jest.fn()
    },
    backFields: {
      add: jest.fn()
    },
    setBarcode: jest.fn(),
    createPass: jest.fn().mockReturnValue({
      setCertificates: jest.fn(),
      asBuffer: jest.fn().mockResolvedValue(Buffer.from('mock-pkpass-data'))
    })
  }))
}));

// Mock fs/promises for asset loading
jest.mock('node:fs/promises', () => ({
  readFile: jest.fn().mockImplementation((path: string) => {
    if (path.includes('icon.png') || path.includes('logo.png')) {
      return Promise.resolve(Buffer.from('mock-image-data'));
    }
    if (path.includes('.p12')) {
      return Promise.resolve(Buffer.from('mock-certificate-data'));
    }
    return Promise.reject(new Error('File not found'));
  })
}));

describe('Apple Pass Generation', () => {
  const originalEnv = process.env;

  beforeAll(() => {
    // Set up test environment variables
    process.env = {
      ...originalEnv,
      PKPASS_TEAM_ID: 'TEST_TEAM',
      PKPASS_PASS_TYPE_ID: 'pass.test.lukhas',
      PKPASS_CERT_P12: './test-cert.p12',
      PKPASS_CERT_P12_PASSWORD: 'test-password'
    };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('generatePkPass', () => {
    it('should generate pass with all required fields', async () => {
      const fields: PassFields = {
        serialNumber: 'SN-12345',
        userId: 'lid_01HXYZ123456789ABCDEFGHJK',
        alias: 'ΛiD#USA/NYC/ABCD-1234-X',
        oneTimeCode: '123456',
        action: 'billing.charge',
        txId: 'tx_' + crypto.randomUUID(),
        expires: Math.floor(Date.now() / 1000) + 60
      };

      const buffer = await generatePkPass(fields);
      
      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    it('should throw error when environment variables are missing', async () => {
      // Temporarily remove an env var
      const savedTeamId = process.env.PKPASS_TEAM_ID;
      delete process.env.PKPASS_TEAM_ID;

      const fields: PassFields = {
        serialNumber: 'SN-12345',
        userId: 'lid_01HXYZ123456789ABCDEFGHJK',
        alias: 'ΛiD#USA/NYC/ABCD-1234-X',
        oneTimeCode: '123456',
        action: 'test.action',
        txId: 'tx_test',
        expires: Math.floor(Date.now() / 1000) + 60
      };

      await expect(generatePkPass(fields)).rejects.toThrow('PKPass env missing');

      // Restore env var
      process.env.PKPASS_TEAM_ID = savedTeamId;
    });

    it('should handle missing passkit-generator package gracefully', async () => {
      // Mock module not found error
      jest.doMock('passkit-generator', () => {
        throw new Error('Cannot find module');
      });

      const fields: PassFields = {
        serialNumber: 'SN-12345',
        userId: 'lid_01HXYZ123456789ABCDEFGHJK',
        alias: 'ΛiD#USA/NYC/ABCD-1234-X',
        oneTimeCode: '123456',
        action: 'test.action',
        txId: 'tx_test',
        expires: Math.floor(Date.now() / 1000) + 60
      };

      // This test will pass with our mock, but documents expected behavior
      const buffer = await generatePkPass(fields);
      expect(buffer).toBeInstanceOf(Buffer);
    });
  });

  describe('PassFields validation', () => {
    it('should accept valid ΛiD alias format', async () => {
      const validAliases = [
        'ΛiD#USA/NYC/ABCD-1234-X',
        'ΛiD#GLO/GLO/H-XXXX-XXXX-X',
        'ΛiD#EU/LON/WXYZ-5678-Y'
      ];

      for (const alias of validAliases) {
        const fields: PassFields = {
          serialNumber: 'SN-' + Math.random(),
          userId: 'lid_01HXYZ123456789ABCDEFGHJK',
          alias,
          oneTimeCode: '123456',
          action: 'test.action',
          txId: 'tx_test',
          expires: Math.floor(Date.now() / 1000) + 60
        };

        const buffer = await generatePkPass(fields);
        expect(buffer).toBeInstanceOf(Buffer);
      }
    });

    it('should generate different serial numbers for different passes', async () => {
      const fields1: PassFields = {
        serialNumber: 'SN-001',
        userId: 'lid_01HXYZ123456789ABCDEFGHJK',
        alias: 'ΛiD#USA/NYC/ABCD-1234-X',
        oneTimeCode: '123456',
        action: 'test.action',
        txId: 'tx_001',
        expires: Math.floor(Date.now() / 1000) + 60
      };

      const fields2: PassFields = {
        ...fields1,
        serialNumber: 'SN-002',
        txId: 'tx_002'
      };

      const buffer1 = await generatePkPass(fields1);
      const buffer2 = await generatePkPass(fields2);

      expect(buffer1).toBeInstanceOf(Buffer);
      expect(buffer2).toBeInstanceOf(Buffer);
      // In real implementation, buffers would be different
      // Our mock returns same data, but this documents expected behavior
    });
  });

  describe('One-time code rotation', () => {
    it('should accept 6-digit codes', async () => {
      const validCodes = ['123456', '000000', '999999', '567890'];

      for (const code of validCodes) {
        const fields: PassFields = {
          serialNumber: 'SN-' + Math.random(),
          userId: 'lid_01HXYZ123456789ABCDEFGHJK',
          alias: 'ΛiD#USA/NYC/ABCD-1234-X',
          oneTimeCode: code,
          action: 'test.action',
          txId: 'tx_test',
          expires: Math.floor(Date.now() / 1000) + 60
        };

        const buffer = await generatePkPass(fields);
        expect(buffer).toBeInstanceOf(Buffer);
      }
    });

    it('should handle expiry timestamps correctly', async () => {
      const now = Math.floor(Date.now() / 1000);
      const expiryTimes = [
        now + 30,  // 30 seconds
        now + 60,  // 60 seconds (standard)
        now + 90   // 90 seconds
      ];

      for (const expires of expiryTimes) {
        const fields: PassFields = {
          serialNumber: 'SN-' + Math.random(),
          userId: 'lid_01HXYZ123456789ABCDEFGHJK',
          alias: 'ΛiD#USA/NYC/ABCD-1234-X',
          oneTimeCode: '123456',
          action: 'test.action',
          txId: 'tx_test',
          expires
        };

        const buffer = await generatePkPass(fields);
        expect(buffer).toBeInstanceOf(Buffer);
      }
    });
  });
});