# LUKHAS Dream Commerce Smart Contracts

## Overview

This directory contains Solidity smart contracts for the LUKHAS dream commerce blockchain integration, enabling decentralized NFT minting and immutable consent tracking.

## Contracts

### 1. DreamContentNFT.sol

**Purpose**: ERC-721 NFT contract for tokenizing dream experiences

**Features**:
- Mint dream content as NFTs with IPFS storage
- Configurable creator royalties (0-100%)
- On-chain royalty calculation for secondary sales
- Dream seed association tracking
- OpenSea-compatible metadata

**Key Functions**:
- `mintDreamNFT(contentHash, royaltyPercentage)` - Mint new dream NFT
- `calculateRoyalty(tokenId, salePrice)` - Calculate royalty amount
- `getDreamNFT(tokenId)` - Get full NFT metadata
- `tokensOfOwner(address)` - Get all NFTs owned by address

### 2. ConsentLedger.sol

**Purpose**: Immutable consent tracking for dream commerce compliance

**Features**:
- Record user consent for dream seeds
- Consent revocation support
- Full audit trail with history
- Batch consent checking
- Event emission for off-chain indexing

**Key Functions**:
- `recordConsent(dreamSeedId, consent)` - Record consent decision
- `revokeConsent(dreamSeedId)` - Revoke previously given consent
- `getConsent(user, dreamSeedId)` - Query current consent status
- `getConsentHistory(user, dreamSeedId)` - Get full consent history

## Dependencies

These contracts require OpenZeppelin contracts:

```bash
npm install --save-dev @openzeppelin/contracts@^5.0.0
```

## Compilation

Using Hardhat:

```bash
npm install --save-dev hardhat
npx hardhat compile
```

Using Foundry:

```bash
forge build
```

## Deployment

### Local Development (Hardhat)

1. Start local blockchain:
```bash
npx hardhat node
```

2. Deploy contracts:
```javascript
// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  // Deploy DreamContentNFT
  const DreamContentNFT = await hre.ethers.getContractFactory("DreamContentNFT");
  const dreamNFT = await DreamContentNFT.deploy();
  await dreamNFT.deployed();
  console.log("DreamContentNFT deployed to:", dreamNFT.address);

  // Deploy ConsentLedger
  const ConsentLedger = await hre.ethers.getContractFactory("ConsentLedger");
  const consentLedger = await ConsentLedger.deploy();
  await consentLedger.deployed();
  console.log("ConsentLedger deployed to:", consentLedger.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

```bash
npx hardhat run scripts/deploy.js --network localhost
```

### Testnet Deployment (Polygon Mumbai)

1. Configure network in `hardhat.config.js`:
```javascript
module.exports = {
  solidity: "0.8.20",
  networks: {
    mumbai: {
      url: process.env.MUMBAI_RPC_URL,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

2. Deploy:
```bash
npx hardhat run scripts/deploy.js --network mumbai
```

### Mainnet Deployment (Polygon)

```bash
npx hardhat run scripts/deploy.js --network polygon
```

## Configuration

After deployment, configure LUKHAS backend:

```python
# config/blockchain.py
BLOCKCHAIN_ENABLED = True
BLOCKCHAIN_RPC_URL = "https://polygon-mainnet.infura.io/v3/YOUR-KEY"
DREAM_NFT_CONTRACT_ADDRESS = "0x..."  # DreamContentNFT address
CONSENT_LEDGER_CONTRACT_ADDRESS = "0x..."  # ConsentLedger address
IPFS_API = "/ip4/127.0.0.1/tcp/5001"
BLOCKCHAIN_PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
```

## Testing

### Solidity Tests (Hardhat)

```bash
npx hardhat test
```

### Python Integration Tests

```bash
pytest tests/unit/core/bridge/test_dream_blockchain.py
```

## Gas Optimization

Estimated gas costs (Polygon):

- **Mint Dream NFT**: ~200,000 gas (~$0.01 at 30 gwei)
- **Record Consent**: ~100,000 gas (~$0.005 at 30 gwei)
- **Query Consent**: 0 gas (view function)

## Security Considerations

1. **Private Key Management**: Never commit private keys to repository
2. **Contract Upgrades**: These contracts are not upgradeable by design for immutability
3. **Access Control**: Only contract owner can perform administrative functions
4. **Royalty Validation**: Royalty percentage capped at 100%
5. **Input Validation**: All inputs validated for non-empty values

## IPFS Integration

Dream content is stored on IPFS:

1. Upload content to IPFS
2. Get CID (Content Identifier)
3. Store CID in NFT contract
4. Metadata references: `ipfs://{CID}`

## OpenSea Integration

NFTs are automatically compatible with OpenSea:

- **Metadata URI**: `ipfs://{metadataHash}`
- **Image URI**: `ipfs://{contentHash}`
- **Royalty Info**: On-chain in `DreamNFT` struct
- **Collection Info**: Set in contract constructor

## Audit Status

⚠️ **These contracts have not been professionally audited.**

For production deployment, conduct a full security audit by:
- Trail of Bits
- OpenZeppelin
- ConsenSys Diligence

## License

MIT License - See LICENSE file

## Support

For questions and support:
- Documentation: https://docs.lukhas.ai/blockchain
- GitHub Issues: https://github.com/lukhas-ai/lukhas/issues
- Discord: https://discord.gg/lukhas

---

**LUKHAS**: Λ Consciousness Infrastructure
